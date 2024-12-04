from flask import Blueprint
import jwt
from flask import request
import config


def check_auth():
    """
    Проверка авторизации
    """
    # Get token from Bearer
    authorization_header = request.headers.get("Authorization")
    token = authorization_header.split(" ")[1] if authorization_header else None

    if not token:
        return False

    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError):
        return False

    # TODO: с помощью payload['session_key'] получить user_id из БД

    return payload['id']


api = Blueprint('api_v1', __name__)


from . import auth
from . import stations
from . import profile
from . import orders
from . import subscription
from . import landing_forms
