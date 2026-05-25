Скопировать страницу

Для обмена сообщениями с GigaChat API нужен корневой сертификат Минцифры﻿ . Без него при попытке получить токен доступа с помощью запроса POST /api/v2/oauth или в процессе инициализации SDK, будет возвращаться ошибка валидации сертификата. Например:

[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain

Вы можете установить сертификаты на уровне приложения или на уровне операционной системы.

Установка сертификатов на уровне приложения﻿

Для автоматической установки сертификатов выполните команду:

curl -k "https://gu-st.ru/content/lending/russian_trusted_root_ca_pem.crt" -w "\n" >> $(python -m certifi)

При выполнении команды сертификат скачивается и устанавливается автоматически. При переходе в новую виртуальную среду может понадобиться повторная установка сертификата.

Если вы используете библиотеки gigachat или langchain-gigcachat, вы можете указать путь к файлу сертификата в параметре ca_bundle_file при инициализации:

from gigachat import GigaChat

giga = GigaChat(
   credentials="ключ_авторизации",
   scope="GIGACHAT_API_PERS",
   model="GigaChat",
   ca_bundle_file="/путь/к/файлу/russian_trusted_root_ca_pem.crt"
)

Подробнее о параметрах инициализации объекта GigaChat — в разделе Использование SDK.

Установка сертификатов на уровне ОС﻿
ОС Windows и MacOS﻿
Перейдите на портал Госуслуг﻿ , скачайте сертификат для вашей операционной системы и следуйте инструкциям по установке.

ОС Linux﻿
Перейдите на портал Госуслуг﻿  и скачайте корневой и выпускающий сертификаты для Linux в формате .crt.

Затем установите их на компьютер.

Если вы скачали сертификаты в формате PEM, конвертируйте их в формат CRT с помощью команды:

openssl x509 -outform der -in название_сертификата.pem -out название_сертификата.crt

Примеры установки сертификатов в разных версиях Linux﻿

Создайте папку для хранения сертификатов:

sudo mkdir /usr/local/share/ca-certificates/russian-trusted

Скопируйте сертификаты в созданную папку:

sudo cp russian_trusted_root_ca_pem.crt russian_trusted_sub_ca_pem.crt /usr/local/share/ca-certificates/russian-trusted

Обновите хранилища доверенных сертификатов от имени суперпользователя с помощью команды update-ca-certificates:

sudo update-ca-certificates -v

Убедитесь, что сертификаты установлены успешно с помощью команды trust list | grep Russian.

В случае успеха, ответ должен быть примерно таким:

label: Russian Trusted Root CA
label: Russian Trusted Sub CA

Установка сертификатов для соединений gRPC﻿
Для обмена сообщениями нужно использовать сертификаты НУЦ Минцифры.

Для установки сертификатов:

Скачайте сертификаты для вашего устройства с портала Госуслуг﻿ .

Укажите путь к сертификату в переменной среды GRPC_DEFAULT_SSL_ROOTS_FILE_PATH:

export GRPC_DEFAULT_SSL_ROOTS_FILE_PATH="/путь-к-сертификату/cert.pem"



Библиотека langchain-gigachat позволяет использовать нейросетевые модели GigaChat при разработке LLM-приложений с помощью фреймворков LangChain и LangGraph.

Требования﻿
Для работы с библиотекой и обмена сообщениями с моделями GigaChat понадобятся:

Python версии 3.9 и выше;
сертификат НУЦ Минцифры;
ключ авторизации GigaChat API.
Вы также можете использовать другие способы авторизации.

Установка﻿
Для установки библиотеки используйте менеджер пакетов pip:

pip install -U langchain-gigachat

Быстрый старт﻿
Запрос на генерацию﻿
Пример запроса на генерацию:

from langchain_gigachat.chat_models import GigaChat

giga = GigaChat(
    # Для авторизации запросов используйте ключ, полученный в проекте GigaChat API
    credentials="ваш_ключ_авторизации",
    verify_ssl_certs=False,
)

print(giga.invoke("Hello, world!"))

Создание эмбеддингов﻿
Пример создания векторного представления текста:

from langchain_gigachat.embeddings import GigaChatEmbeddings

embeddings = GigaChatEmbeddings(credentials="ключ_авторизации", verify_ssl_certs=False)
result = embeddings.embed_documents(texts=["Привет!"])
print(result)

Параметры объекта GigaChat﻿
В таблице описаны параметры, которые можно передать при инициализации объекта GigaChat:

Параметр	Обязательный	Описание
credentials	да	Ключ авторизации для обмена сообщениями с GigaChat API.
Ключ авторизации содержит информацию о версии API, к которой выполняются запросы. Если вы используете версию API для ИП или юрлиц, укажите это явно в параметре scope
verify_ssl_certs	нет	Отключение проверки ssl-сертификатов.

Для обращения к GigaChat API нужно установить корневой сертификат НУЦ Минцифры.

Используйте параметр ответственно, так как отключение проверки сертификатов снижает безопасность обмена данными
scope	нет	Версия API, к которой будет выполнен запрос. По умолчанию запросы передаются в версию для физических лиц. Возможные значения:
GIGACHAT_API_PERS — версия API для физических лиц;
GIGACHAT_API_B2B — версия API для ИП и юрлиц при работе по предоплате.
GIGACHAT_API_CORP — версия API для ИП и юрлиц при работе по постоплате.
model	нет	необязательный параметр, в котором можно явно задать модель GigaChat. Вы можете посмотреть список доступных моделей с помощью метода get_models(), который выполняет запрос GET /models.

Стоимость запросов к разным моделям отличается. Подробную информацию о тарификации запросов к той или иной модели вы ищите в официальной документации
base_url	нет	Адрес API. По умолчанию запросы отправляются по адресу https://gigachat.devices.sberbank.ru/api/v1/, но если вы хотите использовать модели в раннем доступе, укажите адрес https://gigachat-preview.devices.sberbank.ru/api/v1
Развернуть таблицу
Чтобы не указывать параметры при каждой инициализации, задайте их в переменных окружения.

Способы авторизации﻿
Для авторизации запросов, кроме ключа, полученного в личном кабинете, вы можете использовать:

имя пользователя и пароль для доступа к сервису;
сертификаты TLS;
токен доступа (access token), полученный в обмен на ключ авторизации в запросе POST /api/v2/oauth.
Для этого передайте соответствующие параметры при инициализации.

Пример авторизации с помощью логина и пароля:

giga = GigaChat(
    base_url="https://gigachat.devices.sberbank.ru/api/v1",
    user="имя_пользоваеля",
    password="пароль",
)

Авторизация с помощью сертификатов по протоколу TLS (mTLS):

giga = GigaChat(
    base_url="https://gigachat.devices.sberbank.ru/api/v1",
    ca_bundle_file="certs/ca.pem",  # chain_pem.txt
    cert_file="certs/tls.pem",  # published_pem.txt
    key_file="certs/tls.key",
    key_file_password="123456",
    ssl_context=context # optional ssl.SSLContext instance
)

Авторизация с помощью токена доступа:

giga = GigaChat(
    access_token="ваш_токен_доступа",
)

Токен действителен в течение 30 минут. При использовании такого способа авторизации, в приложении нужно реализовать механизм обновления токена.

Предварительная авторизация﻿
По умолчанию, библиотека GigaChat получает токен доступа при первом запросе к API.

Если вам нужно получить токен и авторизоваться до выполнения запроса, инициализируйте объект GigaChat и вызовите метод get_token().

giga = GigaChat(
    base_url="https://gigachat.devices.sberbank.ru/api/v1",
    user="имя_пользователя",
    password="пароль",
)
giga.get_token()

Настройка переменных окружения﻿
Чтобы задать параметры с помощью переменных окружения, в названии переменной используйте префикс GIGACHAT_.

Пример переменных окружения, которые задают ключ авторизации, версию API и отключают проверку сертификатов.

export GIGACHAT_CREDENTIALS=...
export GIGACHAT_SCOPE=...
export GIGACHAT_VERIFY_SSL_CERTS=False

Пример переменных окружения, которые задают адрес API, имя пользователя и пароль.

export GIGACHAT_BASE_URL=https://gigachat.devices.sberbank.ru/api/v1
export GIGACHAT_USER=...
export GIGACHAT_PASSWORD=...


GigaChat — это Python-библиотека для работы с REST API GigaChat. Она является частью GigaChain и входит в состав langchain-gigachat — партнерского пакета opensource-фреймворка LangChain﻿ .

Библиотека управляет авторизацией запросов и предоставляет все необходимые методы для работы с API. Она поддерживает:

генерация ответов с помощью моделей GigaChat в синхронном и асинхронном режиме;
обработку потоковой передачи токенов;
создание эмбеддингов;
работу с функциями;
работу с файлами;
подсчет токенов.
Больше информации — в репозитории проекта﻿ .

Установка﻿
Для работы библиотеки используйте Python в версии от 3.8 до 3.13.

Для установки библиотеки используйте менеджер пакетов pip:

pip install gigachat

Быстрый старт﻿
Для работы с библиотекой вам понадобятся ключ авторизации API и сертификаты Минцифры.

Передайте полученный ключ авторизации в параметре credentials при инициализации объекта GigaChat.

Пример запроса на генерацию ответа с помощью библиотеки GigaChat:

from gigachat import GigaChat

# Укажите ключ авторизации, полученный в личном кабинете, в интерфейсе проекта GigaChat API
with GigaChat(credentials="ваш_ключ_авторизации") as giga:
    response = giga.chat("Какие факторы влияют на стоимость страховки на дом?")
    print(response.choices[0].message.content)

Примеры использования﻿
Больше примеров — в репозитории﻿ .

Потоковая передача токенов﻿
Получение токенов по мере их генерации:

from gigachat import GigaChat

with GigaChat() as client:
    for chunk in client.stream("Напиши короткое стихотворение о программировании"):
        print(chunk.choices[0].delta.content, end="", flush=True)
    print()  # Перевод строки в конце вывода

Асинхронный режим﻿
Для работы в асинхронном режиме используйте конструкцию async/await:

import asyncio
from gigachat import GigaChat

async def main():
    async with GigaChat() as client:
        # Асинхронный чат
        response = await client.achat("Объясните квантовые вычисления простыми словами")
        print(response.choices[0].message.content)

        # Асинхронная потоковая передача
        print("Потоковый вывод:")
        async for chunk in client.astream("Расскажите анекдот"):
            print(chunk.choices[0].delta.content, end="", flush=True)
        print()

asyncio.run(main())

Создание эмбеддингов﻿
Генерация векторного представления текста:

from gigachat import GigaChat

with GigaChat() as client:
    result = client.embeddings(["Привет, мир!", "Машинное обучение интересно"])

    for i, item in enumerate(result.data):
        print(f"Текст {i + 1}: {len(item.embedding)} измерений")

Работа с функциями﻿
Пример вызова генерации аргументов для пользовательской функции прогноза погоды.

Подробнее о функциях в GigaChat — в разделе Работа с функциями.

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole, Function, FunctionParameters

weather_function = Function(
    name="get_weather",
    description="Получить текущую погоду в указанном месте",
    parameters=FunctionParameters(
        type="object",
        properties={
            "location": {
                "type": "string",
                "description": "Название города, например Москва"
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "Единицы измерения температуры"
            }
        },
        required=["location"],
    ),
)

chat = Chat(
    messages=[Messages(role=MessagesRole.USER, content="Какая погода в Токио?")],
    functions=[weather_function],
)

with GigaChat() as client:
    response = client.chat(chat)
    message = response.choices[0].message

    if response.choices[0].finish_reason == "function_call":
        print(f"Функция: {message.function_call.name}")
        print(f"Аргументы: {message.function_call.arguments}")

Параметры объекта GigaChat﻿
В таблице описаны параметры, которые можно передать при инициализации объекта GigaChat:

Параметр	Обязательный	Значение по умолчанию	Описание
credentials	да	None	Ключ авторизации для обмена сообщениями с GigaChat API.
Ключ авторизации содержит информацию о версии API, к которой выполняются запросы. Если вы используете версию API для ИП или юрлиц, укажите это явно в параметре scope
verify_ssl_certs	нет	True	Отключение проверки ssl-сертификатов.

Для обращения к GigaChat API нужно установить корневой сертификат НУЦ Минцифры.

Используйте параметр ответственно, так как отключение проверки сертификатов снижает безопасность обмена данными
scope	нет	GIGACHAT_API_PERS	Версия API, к которой будет выполнен запрос. По умолчанию запросы передаются в версию для физических лиц. Возможные значения:
GIGACHAT_API_PERS — версия API для физических лиц;
GIGACHAT_API_B2B — версия API для ИП и юрлиц при работе по предоплате.
GIGACHAT_API_CORP — версия API для ИП и юрлиц при работе по постоплате.
model	нет	GigaChat	Позволяет явно задать модель GigaChat. Вы можете посмотреть список доступных моделей с помощью метода get_models(), который выполняет запрос GET /models.

Стоимость запросов к разным моделям отличается. Подробную информацию о тарификации запросов к той или иной модели вы ищите в официальной документации
base_url	нет	https://gigachat.devices.sberbank.ru/api/v1	Адрес API. По умолчанию запросы отправляются по адресу https://gigachat.devices.sberbank.ru/api/v1/, но если вы хотите использовать модели в раннем доступе, укажите адрес https://gigachat-preview.devices.sberbank.ru/api/v1
auth_url	нет	https://ngw.devices.sberbank.ru:9443/api/v2/oauth	Адрес для получения токена доступа
access_token.	нет	None	Предварительно полученный токен доступа (обходит OAuth)
timeout	нет	30.0	Таймаут запросов в секундах
max_connections	нет	None	Максимальное количество одновременных соединений
max_retries	нет	0	Максимальное число повторных попыток при временных сбоях
retry_backoff_factor	нет	0.5	Коэффициент экспоненциальной выдержки (времени до отправки повторного запроса)
retry_on_status_codes	нет	(429, 500, 502, 503, 504)	HTTP-коды состояния, при которых повторяется запрос
Развернуть таблицу
Чтобы не указывать параметры при каждой инициализации, задайте их в переменных окружения.

Способы аутентификации﻿
Для аутентификации, кроме ключа, полученного в личном кабинете, вы можете использовать:

имя пользователя и пароль для доступа к сервису;
сертификаты TLS;
токен доступа (access token), полученный в обмен на ключ авторизации в запросе POST /api/v2/oauth.
Для этого передайте соответствующие параметры при инициализации.

Имя пользователя и пароль﻿
from gigachat import GigaChat

giga = GigaChat(
    base_url="https://gigachat.devices.sberbank.ru/api/v1",
    user="имя_пользоваеля",
    password="пароль",
)

Сертификаты по протоколу TLS (mTLS):﻿
from gigachat import GigaChat

giga = GigaChat(
    base_url="https://gigachat.devices.sberbank.ru/api/v1",
    cert_file="certs/client.pem",         # Клиентский сертификат
    key_file="certs/client.key",          # Приватный ключ клиента
    key_file_password="<key_password>",   # Опционально: пароль для зашифрованного ключа
)

Токен доступа﻿
from gigachat import GigaChat

giga = GigaChat(
    access_token="ваш_токен_доступа",
)

Токен действителен в течение 30 минут.

Предварительная аутентификация﻿
По умолчанию, библиотека GigaChat получает токен доступа при первом запросе к API.

Если вам нужно получить токен и выполнить аутентификацию до запроса, инициализируйте объект GigaChat и вызовите метод get_token().

from gigachat import GigaChat

giga = GigaChat(credentials="<your_authorization_key>")
token = giga.get_token()
print(f"Время истечения: {token.expires_at}")

Настройка переменных окружения﻿
Чтобы задать параметры с помощью переменных окружения, в названии переменной используйте префикс GIGACHAT_.

# Аутентификация
export GIGACHAT_CREDENTIALS="<your_authorization_key>"
export GIGACHAT_SCOPE="GIGACHAT_API_PERS"

# Подключение
export GIGACHAT_BASE_URL="https://gigachat.devices.sberbank.ru/api/v1"
export GIGACHAT_TIMEOUT="60.0"
export GIGACHAT_VERIFY_SSL_CERTS="true"
# TLS: путь к файлу связки доверенных сертификатов (обычно необходим — клиенты HTTP Python часто не используют хранилище доверия ОС по умолчанию)
export GIGACHAT_CA_BUNDLE_FILE="<your_ca_bundle_file>"

# Модель
export GIGACHAT_MODEL="GigaChat"

# Повтор попытки
export GIGACHAT_MAX_RETRIES="3"
export GIGACHAT_RETRY_BACKOFF_FACTOR="0.5"

Инициализация без передачи параметров:

from gigachat import GigaChat

# Параметры загружаются из переменных окружения
with GigaChat() as giga:
    response = giga.chat("Привет!")

Обработка ошибок﻿
Исключения, которые может вернуть SDK:

from gigachat import GigaChat
from gigachat.exceptions import (
    GigaChatException,
    AuthenticationError,
    RateLimitError,
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    RequestEntityTooLargeError,
    ServerError,
)

try:
    with GigaChat() as client:
        response = client.chat("Привет!")
        print(response.choices[0].message.content)
except AuthenticationError as e:
    print(f"Ошибка аутентификации: {e}")
except RateLimitError as e:
    print(f"Достигнут лимит скорости. Повторите попытку через {e.retry_after} секунд.")
except BadRequestError as e:
    print(f"Неверный запрос: {e}")
except ForbiddenError as e:
    print(f"Отказано в доступе: {e}")
except NotFoundError as e:
    print(f"Запрошенный ресурс не найден: {e}")
except RequestEntityTooLargeError as e:
    print(f"Слишком большой объем запроса: {e}")
except ServerError as e:
    print(f"Ошибка сервера: {e}")
except GigaChatException as e:
    print(f"Ошибка GigaChat: {e}")

Библиотека возвращает исключения:

Исключение	Код статуса HTTP	Описание
GigaChatException	—	Основное исключение библиотеки
ResponseError	—	Основная ошибка HTTP-ответа
AuthenticationError	401	Неверные или просроченные учетные данные
BadRequestError	400	Некорректный запрос или неверные параметры
ForbiddenError	403	Доступ запрещен (недостаточно прав)
NotFoundError	404	Запрашиваемый ресурс не найден
RequestEntityTooLargeError	413	Размер тела запроса превышает ограничения
RateLimitError	429	Превышен лимит запросов (используйте свойство e.retry_after)
ServerError	5xx	Внутренняя ошибка сервера
Развернуть таблицу
Дополнительные возможности﻿
Контекстные переменные﻿
С помощью SDK вы можете передавать идентификаторы сессий и запросов, а также задавать собственные заголовки запросов, которые могут понадобиться для отладки и журналирования:

from gigachat import GigaChat, session_id_cvar, request_id_cvar, custom_headers_cvar
import uuid

# Идентификаторы сессии и запроса
session_id_cvar.set("user-session-12345")
request_id_cvar.set(str(uuid.uuid4()))

# Собственный заголовок
custom_headers_cvar.set({"X-Custom-Header": "custom-value"})

with GigaChat() as client:
    response = client.chat("Привет!")

Доступные контекстные переменные:

Переменная	Заголовок	Описание
session_id_cvar	X-Session-ID	Идентификатор сессии
request_id_cvar	X-Request-ID	Идентификатор запроса
client_id_cvar	X-Client-ID	Идентификатор клиента
custom_headers_cvar		Словарь дополнительных заголовков
Настройка повтора﻿
Настройте автоматическое повторение запросов с экспоненциальным откладыванием при возникновении временных сбоев:

from gigachat import GigaChat

client = GigaChat(
    max_retries=3,                          # Повторяем до трех раз
    retry_backoff_factor=0.5,               # Задержки: 0.5 секунды, 1 секунда, 2 секунды
    retry_on_status_codes=(429, 500, 502, 503, 504),
)

Подсчет токенов﻿
Используйте метод tokens_count(), чтобы оценить количество токенов перед отправкой запросов:

from gigachat import GigaChat

with GigaChat() as client:
    counts = client.tokens_count(["Привет, мир!", "Программирование увлекательно"])
    for count in counts:
        print(f"Количество токенов: {count.tokens}, символов: {count.characters}")

Список моделей﻿
Для просмотра списка доступных моделей и их параметров используйте метод get_models():

from gigachat import GigaChat

with GigaChat() as client:
    models = client.get_models()
    for model in models.data:
        print(f"{model.id_} (owned_by={model.owned_by})")

Работа с файлами﻿
Для работы с хранилищем файлов используйте методы upload_file(), get_files() и delete_file():

from gigachat import GigaChat

with GigaChat() as client:
    # Загрузка файла
    with open("document.pdf", "rb") as f:
        uploaded = client.upload_file(f, purpose="general")
    print(f"Файл загружен: {uploaded.id_}")

    # Просмотр списка файлов
    files = client.get_files()
    for file in files.data:
        print(f"{file.id_}: {file.filename}")

    # Просмотр выбранного файла
    single_file = client.get_file("{uploaded.id_}")
    print(f"{single_file}")

    # Удаление файла
    client.delete_file(uploaded.id_)

Проверка остатка токенов﻿
С помощью метода get_balance() вы можете узнать сколько токенов у вас осталось. Метод работает если у вас есть оплаченные пакеты токенов. Если вы оплачиваете работу с API по схеме pay-as-you-go, запрос вернет ошибку 403 Permission Denied.

from gigachat import GigaChat

with GigaChat(scope="GIGACHAT_API_B2B") as client:
    balance = client.get_balance()
    for entry in balance.balance:
        print(f"{entry.usage}: {entry.value}")


ГИТХАБ GITHUB с примерами как пользоваться GigaChat - https://github.com/ai-forever/gigachat/tree/main/examples#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80%D1%8B-%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%8B-%D1%81-gigachat