import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.http import HttpRequest
from ninja.security import HttpBearer

class AuthBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str):
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

def generate_jwt(user_id: int) -> str:
    return jwt.encode({
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, settings.JWT_SECRET, algorithm='HS256')