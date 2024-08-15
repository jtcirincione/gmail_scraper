import os
import pickle, time, base64, datetime
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type
from configparser import ConfigParser
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup
from enum import Enum


config = ConfigParser()
config.read('settings.conf')
# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
EMAIL = config.get("General", "email")
RENT = ""
WATER = ""
ELECTRIC = ""

def gmail_authenticate():
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

# get the Gmail API service




def write_csv(file: str) -> None:
    pass

def startup():
    try:
        service = gmail_authenticate()
    except HttpError as err:
        print(err)
    return service

def parse_html(html) -> BeautifulSoup:
    soup = BeautifulSoup(html, 'html.parser')
    # print(soup.body)
    return soup

def handle_subject(subject):
    pass


def handle_date(date):
    pass


def handle_sender(sender) -> bool:
    sender_fr: str = sender['value']
    if 'raleighwater' in sender_fr.lower():
        return True
    return False

def read_messages(service, messages) -> None:
    today = datetime.datetime.now()
    all_messages = []
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        if not msg:
            continue
        tmp_dict = {}
        payload = msg['payload']
        headers = payload.get('headers')
        is_payment = True
        # print(f"headers {headers}")
        for header in headers:
            name: str = header['name']
            if name.lower() == "subject":
                handle_subject(header)
            elif name.lower() == "date":
                handle_date(header)
            elif name.lower() == "sender":
                is_payment = handle_sender(header)
        if not is_payment:
            continue
        parts = msg['payload']['parts']
        for part in parts:
            part_body = part['body']
            part_data = part_body['data']
            html = urlsafe_b64decode(part_data).decode()
            prettified = parse_html(html=html)
            tmp_dict['body'] = prettified
            all_messages.append(tmp_dict)

    print(all_messages)
def main():
    service = startup()


    # print(messages[0])
    while True:
        res = service.users().messages().list(userId="me", labelIds=['INBOX']).execute()
        messages = res['messages']
        print("hellothere")
        
        read_messages(service, messages)
        # sleep to avoid CPU usage
        time.sleep(10)

main()