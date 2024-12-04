from api.v1 import api
from flask import request
import db_helper
import phone_verification
import config
import jwt
import datetime


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
        
        exp = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=365*10)
        encoded_jwt = jwt.encode({"id": user_id, "exp": exp}, config.JWT_SECRET)
        if str(type(encoded_jwt)) == "<class 'bytes'>":
            encoded_jwt = encoded_jwt.decode()
        
        return {"status": "ok", "is_verified": True, "auth_token": encoded_jwt}
    elif res == 'incorrect':
        return {"status": "ok", "is_verified": False, "reason": None}
    elif res == 'attempts_exceeded':
        return {"status": "ok", "is_verified": False, "reason": "attempts_exceeded"}
    elif res == 'timeout_exceeded':
        return {"status": "ok", "is_verified": False, "reason": "timeout_exceeded"}

# TODO: VK auth API
