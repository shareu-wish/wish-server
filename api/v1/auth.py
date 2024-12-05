from api.v1 import api
from flask import request
import db_helper
import phone_verification
import config
import jwt
import datetime
from api.v1 import check_auth
import vk_id_auth


def create_auth_token(user_id):
    exp = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=365*10)
    encoded_jwt = jwt.encode({"id": user_id, "exp": exp}, config.JWT_SECRET)
    if str(type(encoded_jwt)) == "<class 'bytes'>":
        encoded_jwt = encoded_jwt.decode()
    return encoded_jwt


@api.route("/auth/start-phone-verification", methods=["POST"])
def auth_start_phone_verification():
    """
    Вызвать flash-звонок
    """
    # TODO: Капча?
    phone = phone_verification.clean_phone(request.json["phone"])
    phone_verification.verify_phone(phone)

    return {"status": "ok"}


@api.route("/auth/check-code", methods=["POST"])
def auth_check_code():
    """
    Проверить код на достоверность и создать пользователя, если его не существует
    """
    phone = phone_verification.clean_phone(request.json["phone"])
    pincode = request.json["code"]
    res = phone_verification.submit_pincode(phone, pincode)

    if res == 'verified':
        user_id = db_helper.user.get_user_by_phone(phone)
        if not user_id:
            user_id = db_helper.user.create_raw_user(phone)
        else:
            user_id = user_id['id']
        
        encoded_jwt = create_auth_token(user_id)
        
        return {"status": "ok", "is_verified": True, "auth_token": encoded_jwt}
    elif res == 'incorrect':
        return {"status": "ok", "is_verified": False, "reason": None}
    elif res == 'attempts_exceeded':
        return {"status": "ok", "is_verified": False, "reason": "attempts_exceeded"}
    elif res == 'timeout_exceeded':
        return {"status": "ok", "is_verified": False, "reason": "timeout_exceeded"}


@api.route("/auth/vk-id", methods=["POST"])
def auth_vk_id():
    """
    Получает access_token (VK ID), сохраняет данные пользователя, возвращает auth_token (WISH)
    """

    access_token = request.json["access_token"]
    user_info = vk_id_auth.get_user_info(access_token)
    user_info = user_info['user']
    phone = '+' + user_info['phone']

    user_id = db_helper.user.get_user_by_phone(phone)
    if not user_id:
        user_id = db_helper.user.create_raw_user(phone)
    else:
        user_id = user_id['id']

    current_user_data = db_helper.user.get_user(user_id)

    if 'name' in current_user_data and current_user_data['name']:
        name = current_user_data['name']
    else:
        name = user_info['first_name']
    
    if 'age' in current_user_data and current_user_data['age']:
        age = current_user_data['age']
    else:
        # there is only birthday (string) in the user_info
        age = datetime.datetime.now().year - int(user_info['birthday'][-4:])
    
    if 'gender' in current_user_data and current_user_data['gender']:
        gender = current_user_data['gender']
    else:
        if user_info['sex'] == 1:
            gender = 2
        elif user_info['sex'] == 2:
            gender = 1
        else:
            gender = 0

    db_helper.user.update_user_info(user_id, {'name': name, 'age': age, 'gender': gender})

    auth_token = create_auth_token(user_id)
    return {"status": "ok", "auth_token": auth_token}



@api.route("/auth/check")
def auth_check():
    """
    Проверить авторизацию пользователя
    """

    return {"status": "ok", "user_id": check_auth()}

