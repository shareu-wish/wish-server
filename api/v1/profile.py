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


@api.route("/profile/get-active-order")
def profile_get_active_order():
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "order": None}

    order = db_helper.orders.get_active_order(user_id)
    if not order:
        return {"status": "ok", "order": None}

    return {"status": "ok", "order": order}


@api.route("/profile/get-processed-orders")
def profile_get_processed_orders():
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "orders": []}

    orders = db_helper.orders.get_processed_orders(user_id)
    if not orders:
        return {"status": "ok", "orders": []}
    
    for i in range(len(orders)):
        orders[i]['station_take_address'] = db_helper.stations.get_station(orders[i]['station_take'])['address']
        orders[i]['station_put_address'] = db_helper.stations.get_station(orders[i]['station_put'])['address']

    return {"status": "ok", "orders": orders}
