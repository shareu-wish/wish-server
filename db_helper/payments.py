from . import _db_cmd as db_cmd
from datetime import datetime


def get_user_payment_token(user_id: int) -> str | None:
    """
    Получить токен оплаты пользователя

    :param user_id: ID пользователя
    :return: Токен оплаты
    """

    data = db_cmd.fetchone("SELECT payment_token FROM users WHERE id = %s", (user_id, ))

    if data is None:
        return None

    return data[0]


def get_orders_with_delays() -> list[dict]:
    """
    Получить все заказы с задержками

    :return: Список заказов
        - *id*: ID заказа
        - *user_id*: ID пользователя
        - *state*: Статус заказа
        - *deposit_tx_id*: ID транзакции, в которой был сделан депозит
        - *datetime_take*: Дата и время взятия зонт
        - *datetime_last_payment*: Время последнего списания за задержку возврата зонта
        - *payments_for_delay_number*: Количество списаний за задержку
    """

    data = db_cmd.fetchall("SELECT id, user_id, state, deposit_tx_id, datetime_take, datetime_last_payment, payments_for_delay_number FROM orders WHERE state = 1 AND datetime_last_payment < %s - INTERVAL '1 day' AND payments_for_delay_number < 3", (datetime.now(),))

    res = []
    for order in data:
        res.append({
            "id": order[0],
            "user_id": order[1],
            "state": order[2],
            "deposit_tx_id": order[3],
            "datetime_take": order[4],
            "datetime_last_payment": order[5],
            "payments_for_delay_number": order[6]
        })

    return res


def set_order_delay_paid(order_id: int) -> None:
    """
    Установить, что задержка оплачена

    :param order_id: ID заказа
    """

    db_cmd.commit("UPDATE orders SET payments_for_delay_number = payments_for_delay_number + 1, datetime_last_payment = %s WHERE id = %s", (datetime.now(), order_id))
