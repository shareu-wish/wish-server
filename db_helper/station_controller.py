from . import _db_cmd as db_cmd
import config
from datetime import datetime


TIME_TO_TAKE_UMBRELLA = config.TIME_TO_TAKE_UMBRELLA


def set_station_take_umbrella_timeout(order_id: int, station_id: int, slot_id: int) -> None:
    """
    Установить таймаут для взятия зонта

    :param order_id: ID заказа
    :param station_id: ID станции
    :param slot_id: ID слота
    """

    db_cmd.commit("INSERT INTO station_lock_timeouts (order_id, station_id, slot, datetime_opened, type) VALUES (%s, %s, %s, %s, %s)", (order_id, station_id, slot_id, datetime.now(), 1))


def set_station_put_umbrella_timeout(order_id: int, station_id: int, slot_id: int) -> None:
    """
    Установить таймаут для возврата зонта

    :param order_id: ID заказа
    :param station_id: ID станции
    :param slot_id: ID слота
    """

    db_cmd.commit("INSERT INTO station_lock_timeouts (order_id, station_id, slot, datetime_opened, type) VALUES (%s, %s, %s, %s, %s)", (order_id, station_id, slot_id, datetime.now(), 2))


def get_all_station_lock_timeouts() -> list[dict]:
    """
    Найти таймауты для открытия станций

    :return: Список таймаутов
    """

    data = db_cmd.fetchall("SELECT id, order_id, station_id, slot, datetime_opened, type FROM station_lock_timeouts WHERE datetime_opened + interval '%s second' < %s", (TIME_TO_TAKE_UMBRELLA, datetime.now()))

    res = []
    for timeout in data:
        res.append({
            "id": timeout[0],
            "order_id": timeout[1],
            "station_id": timeout[2],
            "slot": timeout[3],
            "datetime_opened": timeout[4],
            "type": timeout[5]
        })

    return res


def get_station_lock_timeout_by_order_id(order_id: int) -> dict | None:
    """
    Найти таймаут открытия станции

    :param order_id: ID заказа
    :return: dict с данными о таймауте\n
        - *id*: ID таймаута
        - *station_id*: ID станции
        - *slot*: ID слота
        - *datetime_opened*: Дата и время открытия
        - *type*: Тип таймаута (1 - взятие зонта, 2 - возврат зонта)
    """

    data = db_cmd.fetchone("SELECT id, station_id, slot, datetime_opened, type FROM station_lock_timeouts WHERE order_id = %s", (order_id,))

    if data is None:
        return None

    res = {
        "id": data[0],
        "station_id": data[1],
        "slot": data[2],
        "datetime_opened": data[3],
        "type": data[4]
    }

    return res


def get_station_lock_timeout_by_station_and_slot(station_id: int, slot: int) -> dict | None:
    """
    Найти таймаут открытия станции

    :param station_id: ID станции
    :param slot: ID слота
    :return: dict с данными о таймауте\n
        - *id*: ID таймаута
        - *order_id*: ID заказа
        - *datetime_opened*: Дата и время открытия
        - *type*: Тип таймаута (1 - взятие зонта, 2 - возврат зонта)
    """

    data = db_cmd.fetchone("SELECT id, order_id, datetime_opened, type FROM station_lock_timeouts WHERE station_id = %s AND slot = %s", (station_id, slot))

    if data is None:
        return None

    res = {
        "id": data[0],
        "order_id": data[1],
        "datetime_opened": data[2],
        "type": data[3]
    }

    return res


def delete_station_lock_timeout(id: int) -> None:
    """
    Удалить таймаут открытия станции

    :param id: ID таймаута
    """

    db_cmd.commit("DELETE FROM station_lock_timeouts WHERE id = %s", (id,))
