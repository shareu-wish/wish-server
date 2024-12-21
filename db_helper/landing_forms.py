from . import _db_cmd as db_cmd


def create_support_request(name: str, city: str, email: str, phone: str, text: str) -> None:
    """
    Создать запись в таблице поддержки

    :param name: Имя
    :param city: Город
    :param email: Email
    :param phone: Номер телефона
    :param text: Текст обращения
    """

    db_cmd.commit("INSERT INTO support (name, city, email, phone, text) VALUES (%s, %s, %s, %s, %s)", (name, city, email, phone, text))


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

    db_cmd.commit("INSERT INTO install_station_requests (name, organization, city, email, phone, text) VALUES (%s, %s, %s, %s, %s, %s)", (name, organization, city, email, phone, text))
