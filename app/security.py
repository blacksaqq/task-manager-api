import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.config import settings

#Настройки безопасности
SECURITY_KEY = settings.security_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


#хэшируем пароль, краткая логика: С помощью ранее написанной пвд контекст мы хэшируем ее по опр стандарту
def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

#проверяем совпадает ли пароль с паролем из базы
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

#Создаем джвт токен для юзера
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire, 'type': 'access'})

    encoded_jwt = jwt.encode(to_encode, SECURITY_KEY, algorithm=ALGORITHM)
    return encoded_jwt 

#декодим этот токен, если с ним что либо делали, то токен будет неавлидным -> вызов ошибки 401
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECURITY_KEY, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError:
        return None
    
#Создаем рефреш токен
def create_refresh_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({'exp': expire, 'type': 'refresh'})

    encoded_jwt = jwt.encode(to_encode, SECURITY_KEY, algorithm=ALGORITHM)
    return encoded_jwt