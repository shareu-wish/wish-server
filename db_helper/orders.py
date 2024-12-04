from db_helper import conn
from datetime import datetime


def open_order(user_id: int, station_id: int, slot: int = None) -> int:
    """
    Создать запись в таблице orders

    :param user_id: ID пользователя
    :param station_id: ID станции
    :param slot: номер слота на станции
    :return: ID заказа
    """

    cur = conn.cursor()
    cur.execute("INSERT INTO orders (user_id, state, station_take, slot_take) VALUES (%s, %s, %s, %s) RETURNING id", (user_id, 1, station_id, slot))
    order_id = cur.fetchone()[0]
    conn.commit()
    cur.close()

    return order_id


def get_active_order(user_id: int) -> dict | None:
    """
    Получить активный заказ пользователя

    :param user_id: ID пользователя
    :return: dict с данными о заказе\n
        - *id*: ID заказа
        - *state*: Статус заказа
        - *datetime_take*: Дата и время взятия зонта
        - *station_take*: ID станции, из которой был взят зонт
        - *slot_take*: номер слота на станции, откуда был взят зонт
        - *deposit_tx_id*: ID транзакции, в которой был сделан депозит
    """

    cur = conn.cursor()
    cur.execute("SELECT id, state, datetime_take, station_take, slot_take, deposit_tx_id FROM orders WHERE user_id = %s AND state = 1", (user_id,))
    data = cur.fetchone()
    cur.close()

    if data is None:
        return None

    res = {
        "id": data[0],
        "state": data[1],
        "datetime_take": data[2],
        "station_take": data[3],
        "slot_take": data[4],
        "deposit_tx_id": data[5]
    }

    return res


def close_order(order_id: int, station_id: int = None, slot: int = None, state: int = 0) -> None:
    """
    Закрыть заказ пользователя

    :param order_id: ID заказа
    :param station_id: ID станции, в которую был помещен зонт
    :param slot: номер слота на станции, куда был помещен зонт
    :param state: Статус заказа\n
        + **0** - заказ закрыт (стандартно)
        + **1** - заказ открыт
        + **2** - заказ закрыт т. к. пользователь не взял зонт вовремя
        + **3** - заказ закрыт из-за проблем с оплатой
        + **4** - заказ закрыт из-за внутренней ошибки (например, нет свободных зонтов)
    """

    cur = conn.cursor()
    cur.execute("UPDATE orders SET state = %s, station_put = %s, slot_put = %s, datetime_put = %s WHERE id = %s", (state, station_id, slot, datetime.now(), order_id))
    conn.commit()
    cur.close()


def get_processed_orders(user_id: int) -> list[dict]:
    """
    Получить все обработанные заказы пользователя

    :param user_id: ID пользователя
    :return: Список заказов\n
        - *id*: ID заказа
        - *state*: Статус заказа
        - *datetime_take*: Дата и время взятия зонта
        - *datetime_put*: Дата и время возврата зонта
        - *station_take*: ID станции, из которой был взят зонт
        - *station_put*: ID станции, в которую был помещен зонт
        - *slot_take*: номер слота на станции, из которой был взят зонт
        - *slot_put*: номер слота на станции, куда был помещен зонт
    """

    cur = conn.cursor()
    cur.execute("SELECT id, state, datetime_take, datetime_put, station_take, station_put, slot_take, slot_put FROM orders WHERE user_id = %s AND state = 0", (user_id, ))
    data = cur.fetchall()
    cur.close()

    res = []
    for order in data:
        res.append({
            "id": order[0],
            "state": order[1],
            "datetime_take": order[2],
            "datetime_put": order[3],
            "station_take": order[4],
            "station_put": order[5],
            "slot_take": order[6],
            "slot_put": order[7]
        })

    return res


def update_order_take_slot(order_id: int, slot: int) -> None:
    """
    Обновить запись в таблице orders

    :param order_id: ID заказа
    :param slot: номер слота на станции, куда был помещен зонт
    """

    cur = conn.cursor()
    cur.execute("UPDATE orders SET slot_take = %s WHERE id = %s", (slot, order_id))
    conn.commit()
    cur.close()


def set_order_deposit_tx_id(order_id: int, tx_id: str) -> None:
    """
    Установить ID транзакции депозита для заказа

    :param order_id: ID заказа
    :param tx_id: ID транзакции, в которой был сделан депозит
    """

    cur = conn.cursor()
    cur.execute("UPDATE orders SET deposit_tx_id = %s WHERE id = %s", (tx_id, order_id))
    conn.commit()
    cur.close()


def get_last_order(user_id: int) -> dict | None:
    """
    Получить последний заказ пользователя

    :param user_id: ID пользователя
    :return: dict с данными о заказе\n
        - *id*: ID заказа
        - *state*: Статус заказа
        - *datetime_take*: Дата и время взятия зонта
        - *datetime_put*: Дата и время возврата зонта
        - *station_take*: ID станции, из которой был взят зонт
        - *station_put*: ID станции, в которую был помещен зонт
        - *slot_take*: номер слота на станции, из которой был взят зонт
        - *slot_put*: номер слота на станции, куда был помещен зонт
    """

    cur = conn.cursor()
    cur.execute("SELECT id, state, datetime_take, datetime_put, station_take, station_put, slot_take, slot_put FROM orders WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    data = cur.fetchone()
    cur.close()

    if data is None:
        return None
    
    res = {
        "id": data[0],
        "state": data[1],
        "datetime_take": data[2],
        "datetime_put": data[3],
        "station_take": data[4],
        "station_put": data[5],
        "slot_take": data[6],
        "slot_put": data[7]
    }
    return res


def get_order(order_id: int) -> dict | None:
    """
    Получить заказ по ID

    :param order_id: ID заказа
    :return: dict с данными о заказе\n
        - *id*: ID заказа
        - *user_id*: ID пользователя
        - *state*: Статус заказа
        - *datetime_take*: Дата и время взятия зонта
        - *station_take*: ID станции, из которой был взят зонт
        - *slot_take*: номер слота на станции, откуда был взят зонт
        - *deposit_tx_id*: ID транзакции, в которой был сделан депозит
    """

    cur = conn.cursor()
    cur.execute("SELECT id, user_id, state, datetime_take, station_take, slot_take, deposit_tx_id FROM orders WHERE id = %s", (order_id,))
    data = cur.fetchone()
    cur.close()

    if data is None:
        return None

    res = {
        "id": data[0],
        "user_id": data[1],
        "state": data[2],
        "datetime_take": data[3],
        "station_take": data[4],
        "slot_take": data[5],
        "deposit_tx_id": data[6]
    }

    return res
