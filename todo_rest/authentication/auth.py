# -*- coding: utf-8 -*-
from rest_framework import authentication
from rest_framework import exceptions
from user.models import Token

from datetime import datetime
from datetime import timedelta

import jwt


FORMAT = "%Y-%m-%d %H:%M:%S"
from todo_rest.settings import JWT_ALGORITHM, TOKEN_EXPIRY, SECRET_KEY as JWT_SECRET

options = {"verify_exp": True}

def jwt_generator(user_id, jwt_secret=JWT_SECRET):
    current_time = datetime.now()
    time = current_time.strftime(FORMAT)
    actual_exp = datetime.strptime(time, FORMAT)

    if TOKEN_EXPIRY >= 0:
        exp_time = current_time + timedelta(milliseconds=TOKEN_EXPIRY)
        exp_at = exp_time.strftime(FORMAT)
        actual_exp = datetime.strptime(exp_at, FORMAT)
    payload = {
        "user_id": user_id,
        "type": "access",
        "issued_at": time,
        "exp": actual_exp.timestamp(),
    }
    jwt_token = jwt.encode(payload, jwt_secret, JWT_ALGORITHM)
    return jwt_token


def jwt_validator(token):
    try:
        payload = jwt.decode(
            token, JWT_SECRET, algorithms=JWT_ALGORITHM, options=options
        )
        return payload
    except Exception as e:
        raise exceptions.AuthenticationFailed

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token_id = request.headers.get("Authorization", "")
        try:
            payload = jwt_validator(token_id)
            Token.objects.get(token=token_id, is_expired=False)
            request.jwt_payload = payload 
            return payload, None
        except Exception:
            raise exceptions.AuthenticationFailed(
                detail={"code": 401, "message": "Expired or Invalid Token"}
            )


