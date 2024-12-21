from . import _db_cmd as db_cmd


def get_stations() -> list[dict]:
    """
    Получить все записи из таблицы stations

    :return: Список станций
    """

    data = db_cmd.fetchall("SELECT id, title, address, latitude, longitude, opening_hours, capacity, can_put, can_take, information, state FROM stations")

    res = []
    for station in data:
        res.append({
            "id": station[0],
            "title": station[1],
            "address": station[2],
            "latitude": station[3],
            "longitude": station[4],
            "opening_hours": station[5],
            "capacity": station[6],
            "can_put": station[7],
            "can_take": station[8],
            "information": station[9],
            "state": station[10]
        })

    return res


def get_station(id: int) -> dict:
    """
    Получить запись из таблицы stations

    :param id: ID станции
    """

    data = db_cmd.fetchone("SELECT id, title, address, latitude, longitude, opening_hours, capacity, can_put, can_take, information, state FROM stations WHERE id = %s", (id,))

    res = {
        "id": data[0],
        "title": data[1],
        "address": data[2],
        "latitude": data[3],
        "longitude": data[4],
        "opening_hours": data[5],
        "capacity": data[6],
        "can_put": data[7],
        "can_take": data[8],
        "information": data[9],
        "state": data[10]
    }

    return res


def decrease_free_umbrellas_on_station(station_id: int) -> None:
    """
    Уменьшить количество свободных зонтов на станции

    :param station_id: ID станции
    """
    
    print("decrease_free_umbrellas_on_station")
    db_cmd.commit("UPDATE stations SET can_take = can_take - 1 WHERE id = %s", (station_id,))
    db_cmd.commit("UPDATE stations SET can_put = can_put + 1 WHERE id = %s", (station_id,))


def increase_free_umbrellas_on_station(station_id: int) -> None:
    """
    Увеличить количество свободных зонтов на станции

    :param station_id: ID станции
    """

    print("increase_free_umbrellas_on_station")
    db_cmd.commit("UPDATE stations SET can_take = can_take + 1 WHERE id = %s", (station_id,))
    db_cmd.commit("UPDATE stations SET can_put = can_put - 1 WHERE id = %s", (station_id,))

