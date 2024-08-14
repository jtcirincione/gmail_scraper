import os
import pickle, time, base64
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

config = ConfigParser()
config.read('settings.conf')
# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
EMAIL = config.get("General", "email")


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
    print(soup.body)
    return soup

def read_messages(service, messages) -> None:
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        payload = msg['payload']
        headers = payload.get('headers')
        # print(f"headers {headers}")
        for header in headers:
            name = header['name']
            # if name.lower() != "from":
            #     print(header)
            #     break
            from_name = header["value"]
            for part in msg['payload']['parts']:
                try:
                    data = part['body']['data']
                    byte_code = base64.urlsafe_b64decode(data)
                    html = byte_code.decode("utf-8")
                    parsed = parse_html(html)
                    with open("./file.html", "w") as f:
                        f.write(parsed.prettify())
                        f.close()
                    print(html)
                    # return
                    # print ("This is the message: "+ str(html))
                except BaseException as err:
                    print(f"unable to decode base64: {err}")
            # return
            # print(email)
        # print(email_data)


def main():
    service = startup()


    # print(messages[0])
    while True:
        res = service.users().messages().list(userId="me", labelIds=['INBOX']).execute()
        messages = res.get('messages', [])
        
        read_messages(service, messages)
        # sleep to avoid CPU usage
        time.sleep(10)

main()