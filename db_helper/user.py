from db_helper import conn


def create_raw_user(phone: str) -> int:
    """
    Создать запись в таблице users

    :param phone: Номер телефона
    :return: ID пользователя
    """

    cur = conn.cursor()
    cur.execute("INSERT INTO users (phone) VALUES (%s)", (phone,))
    conn.commit()
    cur.close()

    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE phone = %s", (phone,))
    user_id = cur.fetchone()[0]
    cur.close()

    return user_id


def get_user(id: int) -> dict:
    """
    Получить запись из таблицы users

    :param id: ID пользователя
    :return: Словарь с данными пользователя\n
        - *id*: ID пользователя
        - *phone*: Номер телефона
        - *name*: Имя
        - *gender*: Пол
        - *age*: Возраст
        - *payment_card_last_four*: Последние 4 цифры платежной карты
    """

    cur = conn.cursor()
    cur.execute("SELECT id, phone, name, gender, age, payment_card_last_four FROM users WHERE id = %s", (id,))
    data = cur.fetchone()
    cur.close()

    res = {
        "id": data[0],
        "phone": data[1],
        "name": data[2],
        "gender": data[3],
        "age": data[4],
        "payment_card_last_four": data[5]
    }

    return res


def get_user_by_phone(phone: str) -> dict | None:
    """
    Получить запись из таблицы users

    :param phone: Номер телефона
    :return: Словарь с данными пользователя или None, если пользователь не найден\n
        - *id*: ID пользователя
        - *phone*: Номер телефона
        - *name*: Имя
        - *gender*: Пол
        - *age*: Возраст
        - *payment_card_last_four*: Последние 4 цифры платежной карты
    """

    cur = conn.cursor()
    cur.execute("SELECT id, phone, name, gender, age, payment_card_last_four FROM users WHERE phone = %s", (phone, ))
    data = cur.fetchone()
    cur.close()

    if data is None:
        return None

    res = {
        "id": data[0],
        "phone": data[1],
        "name": data[2],
        "gender": data[3],
        "age": data[4],
        "payment_card_last_four": data[5]
    }

    return res


def update_user_info(id: int, data: dict) -> None:
    """
    Обновить имя, пол, возраст пользователя

    :param id: ID пользователя
    :param data: Данные пользователя (name, gender, age)
    """

    cur = conn.cursor()
    cur.execute("UPDATE users SET name = %s, gender = %s, age = %s WHERE id = %s", (data["name"], data["gender"], data["age"], id))
    conn.commit()
    cur.close()


def get_user_payment_token(id: int) -> str:
    """
    Получить токен платежа пользователя

    :param id: ID пользователя
    :return: Токен платежа
    """

    cur = conn.cursor()
    cur.execute("SELECT payment_token FROM users WHERE id = %s", (id,))
    data = cur.fetchone()
    cur.close()

    return data[0]


def update_user_payment_token(user_id: int, token: str) -> None:
    """
    Обновить токен платежа пользователя

    :param user_id: ID пользователя
    :param token: Токен платежа
    """

    cur = conn.cursor()
    cur.execute("UPDATE users SET payment_token = %s WHERE id = %s", (token, user_id))
    conn.commit()
    cur.close()


def update_user_payment_card_last_four(id: int, last_four: str) -> None:
    """
    Обновить последние 4 цифры платежной карты пользователя

    :param id: ID пользователя
    :param last_four: Последние 4 цифры платежной карты
    """

    cur = conn.cursor()
    cur.execute("UPDATE users SET payment_card_last_four = %s WHERE id = %s", (last_four, id))
    conn.commit()
    cur.close()
