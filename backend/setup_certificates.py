"""
Скрипт для установки сертификатов НУЦ Минцифры для работы с GigaChat API.
Скачать сертификаты: https://www.gosuslugi.ru/certificates/
"""

import subprocess
import os
import sys


def install_certificates():
    """Установка корневого сертификата Минцифры"""
    
    print("=" * 60)
    print("Установка сертификатов для GigaChat API")
    print("=" * 60)
    
    # Проверка наличия curl
    try:
        subprocess.run(["curl", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Ошибка: curl не установлен. Установите curl или используйте verify_ssl_certs=False")
        return False
    
    cert_url = "https://gu-st.ru/content/lending/russian_trusted_root_ca_pem.crt"
    
    try:
        # Получаем путь к ca-certificates
        result = subprocess.run(
            [sys.executable, "-m", "certifi"],
            capture_output=True,
            text=True,
            check=True
        )
        certifi_path = result.stdout.strip()
        
        print(f"\nПуть к certifi: {certifi_path}")
        print("Скачивание сертификата...")
        
        # Скачиваем и добавляем сертификат
        subprocess.run(
            f'curl -k "{cert_url}" -w "\\n" >> {certifi_path}',
            shell=True,
            check=True
        )
        
        print("\n✓ Сертификат успешно установлен!")
        print("\nДля применения может потребоваться перезапуск терминала/IDE.")
        
    except Exception as e:
        print(f"\nОшибка при установке: {e}")
        print("\nАльтернативный вариант - отключить проверку сертификатов:")
        print("  В файле .env установите: GIGACHAT_VERIFY_SSL_CERTS=False")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    install_certificates()