import imaplib
import email
import re

import requests

# Настройки Gmail
EMAIL_ADDRESS = "testhubkz@gmail.com"
EMAIL_PASSWORD = "plwi nkja sdxp sdiq"
IMAP_SERVER = "imap.gmail.com"

BASE_URL = "https://api.testup.kz"
LOGIN_URL = f"{BASE_URL}/accounts/api/v1/login-email/"
ADD_BALANCE_URL = f"{BASE_URL}/accounts/api/v1/add-balance/"

EMAIL = "yerke@gmail.com"
PASSWORD = "5vvsc7PXe6Uq12n0"

access_token = None


def login():
    global access_token
    r = requests.post(
        LOGIN_URL,
        json={
            "email": EMAIL,
            "password": PASSWORD
        },
        timeout=10
    )
    if r.status_code != 200:
        raise Exception(f"Login failed: {r.text}")

    access_token = r.json()["access"]
    print("🔐 Logged in")


def add_balance_test_up(user_id, balance):
    global access_token

    if not access_token:
        login()

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    r = requests.post(
        ADD_BALANCE_URL,
        json={
            "user_id": user_id,
            "balance": balance
        },
        headers=headers,
        timeout=10
    )

    if r.status_code == 401:
        print("⚠️ Token expired, re-login...")
        login()

        headers["Authorization"] = f"Bearer {access_token}"
        r = requests.post(
            ADD_BALANCE_URL,
            json={
                "user_id": user_id,
                "balance": balance
            },
            headers=headers,
            timeout=10
        )

    if r.status_code != 200:
        raise Exception(f"Add balance failed: {r.text}")

    print("✅ Balance added:", r.json())
    return r.json()


def add_balance():
    from src.accounts.models import BalanceHistory, User
    # Подключение к Gmail по IMAP
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

    # Выбор папки "Входящие"
    mail.select('inbox')

    # Получение списка новых писем
    status, data = mail.search(None, 'UNSEEN', f'FROM "kaspi.payments@kaspibank.kz"')
    mail_ids = data[0]

    # Обработка каждого нового письма
    for mail_id in mail_ids.split():
        status, data = mail.fetch(mail_id, '(RFC822)')
        raw_email = data[0][1]

        # Парсинг письма
        email_message = email.message_from_bytes(raw_email)

        # Извлечение данных из письма
        body = ''
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = email_message.get_payload(decode=True).decode()

        # id_msg = re.search(r"= \d\d\d\d\d\d", body)
        # price_msg = re.search(r"у: \d+\.\d+", body)
        # if id_msg is None:
        #     continue
        # user_id = id_msg.group(0).split(' ')[-1].strip()
        # price = str(price_msg.group(0)).split(' ')[-1].strip()
        id_match = re.search(r'=\s*(\d{6,7})', body)
        price_match = re.search(r'Платеж на сумму:\s*([\d.]+)', body)
        if not id_match or not price_match:
            continue

        user_id = int(id_match.group(1))
        price = float(price_match.group(1))
        if len(str(user_id)) == 7:
            add_balance_test_up(user_id=user_id, balance=int(price))
        else:
            user = User.objects.filter(user_id=int(user_id)).first()
            if user is not None:
                BalanceHistory.objects.create(
                    student=user,
                    balance=int(float(price)),
                    data=body
                )
    # Закрытие соединения
    mail.close()
    mail.logout()
