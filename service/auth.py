import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
import requests
import re
import psycopg2 as pg

cred = credentials.Certificate("service_account.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'backend2023mis.appspot.com'
})

def connect_db():
    return pg.connect(
    dbname="root",
    user="lazzicat",
    password="gwmjblfXfQGH6Xee94FO",
    host="sk8app2024.ch2aea0k4vpx.ap-northeast-1.rds.amazonaws.com",
    port="5432"
    )


def get_user(email):
    try:
        user = auth.get_user_by_email(email)
        return user.uid, user.display_name,user.email
    except:
        return None

def register_user(name, email,password):
    try:
        user = auth.create_user(
        email=email,
        password=password,
        display_name=name,)
        return user.uid
    except Exception as e:
        print(e)
        return None

def authenticate(email,password):
  auth_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key="
  api_key = "AIzaSyBshGP3b1PtFzTuafdT-8aQZ6gPCrENATs"
  
  payload = {
      "email": email,
      "password": password,
      "returnSecureToken": True
  }
  
  response = requests.post(auth_url + api_key, json=payload)
  
  if response.status_code == 200:
      id_token = response.json()["idToken"]
      return id_token
  else:
      print(response.status_code)
      print(response.json())
      return None


async def verify_token(token):
  try:
    decoded_token = auth.verify_id_token(token)
    return decoded_token
  except Exception as e:
      return None


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None