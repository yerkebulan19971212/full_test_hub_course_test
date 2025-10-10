import imaplib
import email
import re

import requests

# Настройки Gmail
EMAIL_ADDRESS = "testhubkz@gmail.com"
EMAIL_PASSWORD = "plwi nkja sdxp sdiq"
IMAP_SERVER = "imap.gmail.com"


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

        id_msg = re.search(r"= \d\d\d\d\d\d", body)
        price_msg = re.search(r"у: \d+\.\d+", body)
        if id_msg is None:
            continue
        user_id = id_msg.group(0).split(' ')[-1].strip()
        price = str(price_msg.group(0)).split(' ')[-1].strip()
        user_id = int(user_id)
        if user_id > 800000:
            requests.post(
                url='https://api-magister.testhub.kz/api/v1/user/add-balance-2/',
                json={
                    "user_id": user_id,
                    "balance": int(float(price))
                }
            )
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
