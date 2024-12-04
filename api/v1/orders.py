from api.v1 import api, check_auth
from flask import request
import db_helper
import station_controller
import payments


@api.route("/orders/take-umbrella", methods=["POST"])
def orders_take_umbrella():
    # TODO: проверить, все ли работает правильно
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "message": "Unauthorized"}
    
    station_id = int(request.json["station_id"])

    can_take = db_helper.stations.get_station(station_id)['can_take']
    if can_take <= 0:
        return {"status": "error", "message": "There are no umbrellas in this station"}
    
    if db_helper.orders.get_active_order(user_id):
        return {"status": "error", "message": "You have an active order"}
    
    # order_id = db_helper.open_order(user_id, station_id)

    # Манипуляции с банками
    payment_token = db_helper.user.get_user_payment_token(user_id)
    if payment_token:
        got_deposit = payments.make_deposit(user_id, station_id)

        if got_deposit:
            return {"status": "ok", "payment_mode": "auto", "user_id": user_id, "station_id": station_id}
        else:
            db_helper.user.update_user_payment_token(user_id, None)
            db_helper.user.update_user_payment_card_last_four(user_id, None)
        
    return {"status": "ok", "payment_mode": "manual", "user_id": user_id, "station_id": station_id}


@api.route("/orders/put-umbrella", methods=["POST"])
def orders_put_umbrella():
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "message": "Unauthorized"}
    
    station_id = int(request.json["station_id"])

    can_put = db_helper.stations.get_station(station_id)['can_put']
    if can_put <= 0:
        return {"status": "error", "message": "There are no empty slots in this station"}
    
    active_order = db_helper.orders.get_active_order(user_id)
    if not active_order:
        return {"status": "error", "message": "You have no active orders"}
    order_id = active_order['id']

    # Манипуляции с аппаратной частью станции
    slot = station_controller.put_umbrella(order_id, station_id)

    return {"status": "ok", "slot": slot, "order_id": order_id}


@api.route("/orders/get-order-status")
def orders_get_order_status():
    """
    Получить текущий статус текущего заказа (если нет текущего, статус последнего заказа)
    """
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "message": "Unauthorized"}
    
    """
    station_opened_to_take - слот открыт для взятия зонта
    station_opened_to_put - слот открыт для возврата зонта
    in_the_hands - зонт взят, находится у пользователя
    closed_successfully - зонт возвращен, заказ закрыт
    timeout_exceeded - время ожидания взятия зонта истекло
    bank_error - ошибка банка, оплата не прошла
    unknown - что-то пошло не так
    """
    
    active_order = db_helper.orders.get_active_order(user_id)
    if active_order:
        timeout = db_helper.station_controller.get_station_lock_timeout_by_order_id(active_order['id'])
        if timeout:
            if timeout['type'] == 1:
                return {"status": "ok", "order_status": "station_opened_to_take", "slot": timeout['slot']}
            elif timeout['type'] == 2:
                return {"status": "ok", "order_status": "station_opened_to_put", "slot": timeout['slot']}
            else:
                return {"status": "ok", "order_status": "unknown"}
        else:
            return {"status": "ok", "order_status": "in_the_hands"}
    else:
        last_order = db_helper.orders.get_last_order(user_id)
        order_status = ""
        if last_order is None:
            order_status = "unknown"
        elif last_order['state'] == 0:
            order_status = "closed_successfully"
        elif last_order['state'] == 2:
            order_status = "timeout_exceeded"
        elif last_order['state'] == 3:
            order_status = "bank_error"
        else:
            order_status = "unknown"
        
        return {"status": "ok", "order_status": order_status}
    

@api.route("/orders/feedback", methods=["POST"])
def orders_feedback():
    """
    Оставить отзыв на последний заказ
    """
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "message": "Unauthorized"}
    
    order_id = db_helper.orders.get_last_order(user_id)['id']
    rate = request.json["rate"]
    text = request.json["text"]

    if rate < 1 or rate > 5:
        return {"status": "error", "message": "Invalid rate"}
    if db_helper.order_feedback.has_user_feedback(user_id, order_id):
        return {"status": "error", "message": "Feedback for this order has already been left"}

    db_helper.order_feedback.create_order_feedback(user_id, order_id, rate, text)

    return {"status": "ok"}
