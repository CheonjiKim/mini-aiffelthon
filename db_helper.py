import sqlite3
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

DB_FILE = "auth.db"

# 데이터베이스 초기화
def init_db():
    """SQLite 데이터베이스 초기화"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS google_auth (
            user_email TEXT PRIMARY KEY,
            credentials TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# 인증 정보 저장
def save_credentials(credentials, user_email="user_email"):
    """사용자 인증 정보를 SQLite에 저장"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    serialized_credentials = json.dumps({
        'user_profile': credentials.user_profile,
        'user_email': credentials.user_email,
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    })
    print("DEBUG: Saving credentials:", serialized_credentials)
    cursor.execute('REPLACE INTO google_auth (user_email, credentials) VALUES (?, ?)', (user_email, serialized_credentials))
    conn.commit()
    conn.close()

# 인증 정보 불러오기
def load_credentials(user_email="user_email"):
    """SQLite에서 사용자 인증 정보를 불러오기"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT credentials FROM google_auth WHERE user_email = ?', (user_email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        credentials_info = json.loads(row[0])
        credentials = Credentials.from_authorized_user_info(credentials_info)
        print("DEBUG: Loaded credentials:", credentials_info)
        # 만료된 토큰 갱신
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            save_credentials(credentials, user_email)
        return credentials
    return None

# 인증 정보 존재 여부 확인
def is_authenticated(user_email="user_email"):
    """사용자 인증 여부 확인"""
    credentials = load_credentials(user_email)
    print("DEBUG: Checking authentication for user:", user_email)
    print("DEBUG: Loaded credentials:", credentials)
    return credentials is not None and not (credentials.expired and not credentials.refresh_token)  
