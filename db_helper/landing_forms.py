from db_helper import conn


def create_support_request(name: str, city: str, email: str, phone: str, text: str) -> None:
    """
    Создать запись в таблице поддержки

    :param name: Имя
    :param city: Город
    :param email: Email
    :param phone: Номер телефона
    :param text: Текст обращения
    """

    cur = conn.cursor()
    cur.execute("INSERT INTO support (name, city, email, phone, text) VALUES (%s, %s, %s, %s, %s)", (name, city, email, phone, text))
    conn.commit()
    cur.close()


def create_install_station_request(name: str, organization: str, city: str, email: str, phone: str, text: str) -> None:
    """
    Создать запись в таблице с заявками на установку станции

    :param name: Имя того, кто оставляет заявку
    :param organization: Название организации
    :param city: Город
    :param email: Email
    :param phone: Номер телефона
    :param text: Комментарий
    """

    cur = conn.cursor()
    cur.execute("INSERT INTO install_station_requests (name, organization, city, email, phone, text) VALUES (%s, %s, %s, %s, %s, %s)", (name, organization, city, email, phone, text))
    conn.commit()
    cur.close()
