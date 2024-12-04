from db_helper import conn
from threading import Timer
from datetime import datetime
import config


def create_verify_phone_record(phone: str, pincode: str) -> None:
    """
    Создать запись в таблице user_verification

    :param phone: Номер телефона
    :param pincode: Пинкод
    """

    cur = conn.cursor()
    cur.execute("INSERT INTO user_verification (phone, pincode) VALUES (%s, %s)", (phone, pincode))
    conn.commit()
    cur.close()


def get_verify_phone_record(phone: str) -> tuple[str]:
    """
    Получить запись из таблицы user_verification

    :param phone: Номер телефона
    :return: tuple (phone, pincode)
    """

    cur = conn.cursor()
    cur.execute("SELECT phone, pincode FROM user_verification WHERE phone = %s", (phone,))
    result = cur.fetchone()
    cur.close()

    return result


def update_verify_phone_record(phone: str, pincode: str) -> None:
    """
    Обновить запись в таблице user_verification

    :param phone: Номер телефона
    :param pincode: Пинкод
    """

    cur = conn.cursor()
    cur.execute("UPDATE user_verification SET pincode = %s, attempts = 0 WHERE phone = %s", (pincode, phone))
    conn.commit()
    cur.close()


def delete_verify_phone_record(phone: str) -> None:
    """
    Удалить запись из таблицы user_verification

    :param phone: Номер телефона
    """

    cur = conn.cursor()
    cur.execute("DELETE FROM user_verification WHERE phone = %s", (phone, ))
    conn.commit()
    cur.close()


def increment_attempts(phone: str) -> int:
    """
    Увеличить количество попыток в таблице user_verification

    :param phone: Номер телефона
    :return: Количество попыток
    """

    cur = conn.cursor()
    cur.execute("UPDATE user_verification SET attempts = attempts + 1 WHERE phone = %s", (phone,))
    conn.commit()
    cur.close()

    cur = conn.cursor()
    cur.execute("SELECT attempts FROM user_verification WHERE phone = %s", (phone,))
    attempts = cur.fetchone()[0]
    cur.close()
    
    return attempts


def _delete_old_data() -> None:
    """
    Удалить старые записи из таблицы user_verification
    """

    cur = conn.cursor()
    cur.execute("DELETE FROM user_verification WHERE created_at < %s - INTERVAL '10 minute'", (datetime.now(),))
    conn.commit()
    cur.close()


def _schedule_delete_old_data() -> None:
    """
    Запланировать удаление старых записей
    """
    _delete_old_data()
    Timer(60*2, _schedule_delete_old_data).start()



if not config.DEBUG:
    _schedule_delete_old_data()
