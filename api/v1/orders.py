from api.v1 import api, check_auth
from flask import request
import db_helper
import station_controller
import payments
import json
import config


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


@api.route("/orders/take-umbrella/success-payment", methods=["POST"])
def take_umbrella_success_payment():
    """
    CloudPayments должны присылвать сюда ответ
    """
    raw_data = request.get_data().decode()
    if not payments.is_notification_valid(request.headers.get('Content-HMAC'), raw_data):
        return {"code": 1}

    data = request.form
    # print(data.data)
    user_id = data.get("AccountId")
    # order_id = data.get("InvoiceId")
    currency = data.get("PaymentCurrency")
    amount = data.get("PaymentAmount")
    tx_id = data.get("TransactionId")
    token = data.get("Token")
    card_last_four = data.get("CardLastFour")
    custom_data = data.get("Data")
    payment_type = ""
    if custom_data:
        custom_data = json.loads(custom_data)
        # payment_mode = custom_data["paymentMode"]
        payment_type = custom_data["paymentType"]
        station_take = custom_data["stationTake"]

    if payment_type != "deposit":
        return {"code": 0}
    
    if currency != "RUB" or float(amount) != config.DEPOSIT_AMOUNT:
        print("Invalid payment")
        payments.refund_deposit_by_tx_id(tx_id)
        return {"code": 0}
    
    if not station_take and station_take != 0:
        print("Invalid station_take")
        payments.refund_deposit_by_tx_id(tx_id)
        return {"code": 0}
    
    real_active_order = db_helper.orders.get_active_order(user_id)
    if real_active_order:
        print("Invalid order")
        payments.refund_deposit_by_tx_id(tx_id)
        return {"code": 0}
    
    order_id = db_helper.orders.open_order(user_id, station_take)

    db_helper.user.update_user_payment_token(user_id, token)
    db_helper.user.update_user_payment_card_last_four(user_id, card_last_four)
    db_helper.orders.set_order_deposit_tx_id(order_id, tx_id)
    
    # Манипуляции с аппаратной частью станции
    slot = station_controller.give_out_umbrella(order_id, station_take)
    if slot is None:
        db_helper.orders.close_order(order_id, state=4)
        print("Failed to take an umbrella")
        return {"status": "error", "message": "Failed to take an umbrella"}
    
    db_helper.orders.update_order_take_slot(order_id, slot)

    return {"code": 0}


@api.route("/orders/take-umbrella/fail-payment", methods=["POST"])
def take_umbrella_fail_payment():
    print("take_umbrella_fail_payment")
    raw_data = request.get_data().decode()
    if not payments.is_notification_valid(request.headers.get('Content-HMAC'), raw_data):
        return {"code": 1}

    data = request.form
    user_id = data.get("AccountId")

    db_helper.user.update_user_payment_token(user_id, None)
    db_helper.user.update_user_payment_card_last_four(user_id, None)

    return {"code": 0}


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


@api.route("/orders/get-active-order")
def get_active_order():
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "message": "Unauthorized", "order": None}

    order = db_helper.orders.get_active_order(user_id)
    if not order:
        return {"status": "ok", "order": None}

    return {"status": "ok", "order": order}


@api.route("/orders/get-processed-orders")
def get_processed_orders():
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "message": "Unauthorized", "orders": []}

    orders = db_helper.orders.get_processed_orders(user_id)
    if not orders:
        return {"status": "ok", "orders": []}
    
    for i in range(len(orders)):
        orders[i]['station_take_address'] = db_helper.stations.get_station(orders[i]['station_take'])['address']
        orders[i]['station_put_address'] = db_helper.stations.get_station(orders[i]['station_put'])['address']

    return {"status": "ok", "orders": orders}
