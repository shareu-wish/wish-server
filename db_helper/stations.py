from db_helper import conn


def get_stations() -> list[dict]:
    """
    Получить все записи из таблицы stations

    :return: Список станций
    """

    cur = conn.cursor()
    cur.execute("SELECT id, title, address, latitude, longitude, opening_hours, capacity, can_put, can_take, picture, information, state FROM stations")
    data = cur.fetchall()
    cur.close()

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
            "picture": station[9],
            "information": station[10],
            "state": station[11]
        })

    return res


def get_station(id: int) -> dict:
    """
    Получить запись из таблицы stations

    :param id: ID станции
    """

    cur = conn.cursor()
    cur.execute("SELECT id, title, address, latitude, longitude, opening_hours, capacity, can_put, can_take, picture, information, state FROM stations WHERE id = %s", (id,))
    data = cur.fetchone()
    cur.close()

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
        "picture": data[9],
        "information": data[10],
        "state": data[11]
    }

    return res


def decrease_free_umbrellas_on_station(station_id: int) -> None:
    """
    Уменьшить количество свободных зонтов на станции

    :param station_id: ID станции
    """
    
    print("decrease_free_umbrellas_on_station")
    cur = conn.cursor()
    cur.execute("UPDATE stations SET can_take = can_take - 1 WHERE id = %s", (station_id,))
    cur.execute("UPDATE stations SET can_put = can_put + 1 WHERE id = %s", (station_id,))
    conn.commit()
    cur.close()


def increase_free_umbrellas_on_station(station_id: int) -> None:
    """
    Увеличить количество свободных зонтов на станции

    :param station_id: ID станции
    """

    print("increase_free_umbrellas_on_station")
    cur = conn.cursor()
    cur.execute("UPDATE stations SET can_take = can_take + 1 WHERE id = %s", (station_id,))
    cur.execute("UPDATE stations SET can_put = can_put - 1 WHERE id = %s", (station_id,))
    conn.commit()
    cur.close()
