from api.v1 import api, check_auth
from flask import request
import db_helper


@api.route('/profile/get-user-info')
def profile_get_user_info():
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "message": "Unauthorized"}
    
    data = db_helper.user.get_user(user_id)
    res = {
        "id": data['id'],
        "phone": data['phone'],
        "name": data['name'],
        "gender": data['gender'],
        "age": data['age'],
        "payment_card_last_four": data['payment_card_last_four']
    }
    return res


@api.route('/profile/update-user-info', methods=['POST'])
def profile_update_user_info():
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "message": "Unauthorized"}
    
    data = request.get_json(force=True)
    db_helper.user.update_user_info(user_id, data)
    
    return {"status": "ok"}
