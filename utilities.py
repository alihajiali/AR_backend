from datetime import datetime, timedelta
from uuid import uuid4
from env import *
import requests
import hashlib
import jwt



def hash_saz(matn):
    return hashlib.sha256(str.encode()).hexdigest()




def send_sms(phone_number, text):
    response = requests.post(SMS_IR_URL, headers={"X-API-KEY":API_KEYS_SMS_IR}, 
    json={"lineNumber": PHONE_NUMBER, "messageText": text, "mobiles": [phone_number], "sendDateTime": None})
    return response.status_code




def generate_code(username):
    if redis_cli.exists(username) == 0:
        code = str(uuid4().int)[:5]
        redis_cli.set(username, code, ex=120)
        return code
    return False

def check_code(username, code):
    if redis_cli.get(username) == code:
        return True
    return False




def jwt_generator(username):
    expire = (datetime.now() + timedelta(minutes=1)).isoformat()
    token = jwt.encode({"username":username, "expire":expire}, DJANGO_SECRET_KEY, algorithm="HS256")
    return token.decode()

def jwt_checker(token):
    data = jwt.decode(token.encode(), DJANGO_SECRET_KEY, algorithms=["HS256"])
    return data

print(jwt_generator("username"))

def Auth(jwt_json):
    if datetime.now().isoformat() < jwt_json["expire"]:
        return True
    return False