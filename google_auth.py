import os
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from db_helper import save_credentials, load_credentials
 
SCOPES = [
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

import requests

def get_user_informations(credentials):
    """Google 사용자 프로필 정보 가져오기"""
    headers = {'Authorization': f'Bearer {credentials.token}'}
    response = requests.get('https://www.googleapis.com/oauth2/v1/userinfo', headers=headers)
    if response.ok:
        return response.json()  # contains 'id', 'email', 'name', etc.
    else:
        raise Exception("Failed to fetch user info", response.text)

def create_oauth_flow(redirect_uri):
    """OAuth 인증 흐름 생성"""
    client_config = {
        "web": {
            "user_profile": "https://www.googleapis.com/auth/userinfo.profile",
            "user_email": "https://www.googleapis.com/auth/userinfo.email",
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri]
        }
    }
    return Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=redirect_uri)

def get_authorization_url(flow):
    """인증 URL 생성"""
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return auth_url

def fetch_token(flow, code):
    """인증 코드로 토큰 가져오기"""
    flow.fetch_token(code=code)
    credentials = flow.credentials
    user_info = get_user_informations(credentials)
    user_email = user_info['email']
    save_credentials(credentials, user_email)
    print("DEBUG: User info:", user_info)
    print("DEBUG: User email:", user_email)
    return credentials

def is_authenticated(user_email="no email"):
    """사용자 인증 여부 확인"""
    credentials = load_credentials(user_email)
    if credentials:
        # 토큰이 만료된 경우 갱신
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            save_credentials(credentials, user_email)
        return True
    return False

def build_gmail_service(credentials):
    """Gmail API 서비스 생성"""
    return build('gmail', 'v1', credentials=credentials)

def build_calendar_service(credentials):
    """Calendar API 서비스 생성"""
    return build('calendar', 'v3', credentials=credentials)