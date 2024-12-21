from . import _db_cmd as db_cmd


def create_raw_user(phone: str) -> int:
    """
    Создать запись в таблице users

    :param phone: Номер телефона
    :return: ID пользователя
    """

    db_cmd.commit("INSERT INTO users (phone) VALUES (%s)", (phone,))
    user_id = db_cmd.fetchone("SELECT id FROM users WHERE phone = %s", (phone,))[0]

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

    data = db_cmd.fetchone("SELECT id, phone, name, gender, age, payment_card_last_four FROM users WHERE id = %s", (id,))

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

    data = db_cmd.fetchone("SELECT id, phone, name, gender, age, payment_card_last_four FROM users WHERE phone = %s", (phone,))

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

    db_cmd.commit("UPDATE users SET name = %s, gender = %s, age = %s WHERE id = %s", (data["name"], data["gender"], data["age"], id))


def get_user_payment_token(id: int) -> str:
    """
    Получить токен платежа пользователя

    :param id: ID пользователя
    :return: Токен платежа
    """

    data = db_cmd.fetchone("SELECT payment_token FROM users WHERE id = %s", (id,))

    return data[0]


def update_user_payment_token(user_id: int, token: str) -> None:
    """
    Обновить токен платежа пользователя

    :param user_id: ID пользователя
    :param token: Токен платежа
    """

    db_cmd.commit("UPDATE users SET payment_token = %s WHERE id = %s", (token, user_id))


def update_user_payment_card_last_four(id: int, last_four: str) -> None:
    """
    Обновить последние 4 цифры платежной карты пользователя

    :param id: ID пользователя
    :param last_four: Последние 4 цифры платежной карты
    """

    db_cmd.commit("UPDATE users SET payment_card_last_four = %s WHERE id = %s", (last_four, id))
