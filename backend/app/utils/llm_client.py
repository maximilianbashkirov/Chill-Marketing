import json
import logging
import re
from typing import Dict, Any, List, Optional, Type, TypeVar
from pydantic import BaseModel
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
from gigachat.exceptions import (
    GigaChatException,
    AuthenticationError,
    RateLimitError,
    BadRequestError,
    ServerError,
)
from ..config import settings

logger = logging.getLogger(__name__)
T = TypeVar('T', bound=BaseModel)


class LLMClient:
    """Client for working with GigaChat API with structured output support"""
    
    def __init__(self):
        self.credentials = settings.GIGACHAT_CREDENTIALS
        self.base_url = settings.GIGACHAT_BASE_URL
        self.verify_ssl_certs = settings.GIGACHAT_VERIFY_SSL_CERTS
        self.scope = settings.GIGACHAT_SCOPE
        self.model = settings.GIGACHAT_MODEL
        self.timeout = settings.GIGACHAT_TIMEOUT
        self.proxy = settings.GIGACHAT_PROXY
    
    def _get_client(self) -> Optional[GigaChat]:
        """Get GigaChat client instance"""
        if not self.credentials:
            return None
        
        import httpx
        
        # Create HTTP client with proxy if configured
        http_client = None
        if self.proxy:
            http_client = httpx.Client(
                proxy=self.proxy,
                timeout=self.timeout
            )
        
        return GigaChat(
            credentials=self.credentials,
            base_url=self.base_url,
            verify_ssl_certs=self.verify_ssl_certs,
            scope=self.scope,
            model=self.model,
            timeout=self.timeout,
            max_retries=3,
            retry_backoff_factor=0.5,
            http_client=http_client,
        )
    
    def _build_messages(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> List[Messages]:
        """Build messages list for chat"""
        messages = []
        
        if system_prompt:
            messages.append(Messages(role=MessagesRole.SYSTEM, content=system_prompt))
        
        messages.append(Messages(role=MessagesRole.USER, content=prompt))
        
        return messages
    
    async def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Send chat request to GigaChat
        Returns text response from the model
        """
        if not self._get_client():
            return self._get_mock_response(prompt)
        
        messages = self._build_messages(prompt, system_prompt)
        
        try:
            with self._get_client() as client:
                chat = Chat(messages=messages)
                response = client.chat(chat)
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f"GigaChat API error: {e}")
            return self._get_mock_response(prompt)
    
    async def chat_parse(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        strict: bool = True,
        temperature: float = 0.3
    ) -> T:
        """
        Send chat request with structured output using Pydantic model.
        Uses GigaChat's native JSON schema support.
        
        Args:
            prompt: User prompt
            response_model: Pydantic BaseModel class for response
            system_prompt: Optional system prompt
            strict: Use strict JSON schema (default True)
            temperature: Temperature setting
            
        Returns:
            Parsed Pydantic model instance
        """
        if not self._get_client():
            return self._get_mock_parsed_response(response_model)
        
        messages = self._build_messages(prompt, system_prompt)
        
        chat = Chat(
            messages=messages,
            response_format={
                "type": "json_schema",
                "schema": response_model,
                "strict": strict,
            },
        )
        
        try:
            with self._get_client() as client:
                resp = client.chat(chat)
                data = json.loads(resp.choices[0].message.content)
                return response_model.model_validate(data)
        except Exception as e:
            logger.error(f"GigaChat chat_parse error: {e}")
            return self._get_mock_parsed_response(response_model)
    
    @staticmethod
    def _clean_json_response(response: str) -> str:
        """Очищает ответ GigaChat от обёрток, trailing commas и невалидных чисел перед парсингом"""
        # Удаляем markdown-блоки ```json ... ```
        result = re.sub(r'```(?:json)?\s*', '', response)
        result = result.strip()
        if result.endswith('```'):
            result = result[:-3].strip()

        # Контекстно-зависимое удаление trailing commas (внутри строк не трогаем)
        chars = []
        in_string = False
        escape = False
        i = 0
        while i < len(result):
            ch = result[i]
            if escape:
                escape = False
                chars.append(ch)
            elif ch == '\\' and in_string:
                escape = True
                chars.append(ch)
            elif ch == '"':
                in_string = not in_string
                chars.append(ch)
            elif not in_string and ch == ',':
                j = i + 1
                while j < len(result) and result[j] in ' \t\n\r':
                    j += 1
                if j < len(result) and result[j] in '}]':
                    i = j - 1
                else:
                    chars.append(ch)
            else:
                chars.append(ch)
            i += 1
        result = ''.join(chars)

        # Убираем подчёркивания внутри чисел (1_200_000 → 1200000)
        result = re.sub(r'(?<=\d)_(?=\d)', '', result)

        return result

    async def chat_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 6000
    ) -> Dict[str, Any]:
        """
        Send chat request and parse response as JSON (legacy method).
        Use chat_parse with Pydantic models for better results.
        """
        json_prompt = f"{prompt}\n\nОтветь только в формате JSON без дополнительного текста."

        response = await self.chat(
            prompt=json_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Пробуем распарсить "как есть" — часто GigaChat уже выдаёт валидный JSON
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass

        cleaned = self._clean_json_response(response)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            pos = e.pos
            start = max(0, pos - 100)
            end = min(len(cleaned), pos + 100)
            logger.error(
                f"chat_json parse error at position {pos}: "
                f"context=[{cleaned[start:end]}]  "
                f"response_len={len(response)} cleaned_len={len(cleaned)}"
            )
            # Финальная попытка — ищем `{...}` через регулярку на случай мусора вокруг JSON
            brace_match = re.search(r'\{[^{}]*(\{[^{}]*\}[^{}]*)*\}', cleaned)
            if brace_match:
                try:
                    return json.loads(brace_match.group())
                except json.JSONDecodeError:
                    pass
            return {"error": "Failed to parse JSON", "raw_response": response}
    
    def _get_mock_response(self, prompt: str) -> str:
        """Return mock response when GigaChat is not configured"""
        return "GigaChat не настроен. Пожалуйста, добавьте GIGACHAT_CREDENTIALS в .env файл."
    
    def _get_mock_parsed_response(self, response_model: Type[T]) -> T:
        """Return mock parsed response when GigaChat is not configured"""
        # Return empty model instance
        return response_model.model_validate({})


llm_client = LLMClient()