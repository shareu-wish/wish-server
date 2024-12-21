from . import _db_cmd as db_cmd
from threading import Timer
from datetime import datetime
import config


def create_verify_phone_record(phone: str, pincode: str) -> None:
    """
    Создать запись в таблице user_verification

    :param phone: Номер телефона
    :param pincode: Пинкод
    """

    db_cmd.commit("INSERT INTO user_verification (phone, pincode) VALUES (%s, %s)", (phone, pincode))


def get_verify_phone_record(phone: str) -> tuple[str]:
    """
    Получить запись из таблицы user_verification

    :param phone: Номер телефона
    :return: tuple (phone, pincode)
    """

    result = db_cmd.fetchone("SELECT phone, pincode FROM user_verification WHERE phone = %s", (phone,))
    return result


def update_verify_phone_record(phone: str, pincode: str) -> None:
    """
    Обновить запись в таблице user_verification

    :param phone: Номер телефона
    :param pincode: Пинкод
    """

    db_cmd.commit("UPDATE user_verification SET pincode = %s, attempts = 0 WHERE phone = %s", (pincode, phone))


def delete_verify_phone_record(phone: str) -> None:
    """
    Удалить запись из таблицы user_verification

    :param phone: Номер телефона
    """

    db_cmd.commit("DELETE FROM user_verification WHERE phone = %s", (phone,))


def increment_attempts(phone: str) -> int:
    """
    Увеличить количество попыток в таблице user_verification

    :param phone: Номер телефона
    :return: Количество попыток
    """

    db_cmd.commit("UPDATE user_verification SET attempts = attempts + 1 WHERE phone = %s", (phone,))

    attempts = db_cmd.fetchone("SELECT attempts FROM user_verification WHERE phone = %s", (phone,))[0]
    
    return attempts


def _delete_old_data() -> None:
    """
    Удалить старые записи из таблицы user_verification
    """

    db_cmd.commit("DELETE FROM user_verification WHERE created_at < %s - INTERVAL '10 minute'", (datetime.now(),))


def _schedule_delete_old_data() -> None:
    """
    Запланировать удаление старых записей
    """
    _delete_old_data()
    Timer(60*2, _schedule_delete_old_data).start()



if not config.DEBUG:
    _schedule_delete_old_data()
