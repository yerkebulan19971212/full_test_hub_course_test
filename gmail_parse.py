from __future__ import print_function

import base64
import email
import os.path
import re
import sched
import time
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
MODIFY_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

s = sched.scheduler(time.time, time.sleep)


def get_message(service, user_id, msg_id):
    msg = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
    msg_raw = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
    msg_str = email.message_from_bytes(msg_raw)
    content_types = msg_str.get_content_maintype()
    if content_types == 'multipart':
        part1, part2 = msg_str.get_payload()
        body_text = str(part1).split("\n\n")[-1]
    else:
        body_text = str(msg_str.get_payload())
    sample_string_bytes = base64.b64decode(body_text)
    sample_string = sample_string_bytes.decode("utf-8")
    return sample_string


def as_read_message(msg_id):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', MODIFY_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', MODIFY_SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)

    msg = service.users().messages().modify(userId='me', id=msg_id, body={"removeLabelIds": ["UNREAD"]}).execute()


def main(sc):
    creds = None
    if os.path.exists('read_token.json'):
        creds = Credentials.from_authorized_user_file('read_token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('read_token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q="from:kaspi.payments@kaspibank.kz is:unread"
    ).execute()
    messages = results.get('messages', [])
    if not messages:
        print("You have no new messages.")
    else:
        for message in messages:
            msg = get_message(service=service,
                              user_id='me',
                              msg_id=message['id'])
            id_msg = re.search(r"= \d\d\d\d", msg)
            price_msg = re.search(r"у: \d+\.\d+", msg)
            if id_msg is None:
                continue
            user_id = id_msg.group(0).split(' ')[-1]
            price = str(price_msg.group(0)).split(' ')[-1]

            url = 'https://api-ent.testhub.kz/api/v1/user/add-balance-api/'
            data = {
                'balance': price,
                'user_id': user_id,
            }
            req = requests.post(url, data=data)
            if req.status_code == 201:
                as_read_message(message['id'])
    if not messages:
        print('No messages found')
    s.enter(120, 1, main, (sc,))


if __name__ == '__main__':
    s.enter(1, 1, main, (s,))
    s.run()
# as_read_message(1)