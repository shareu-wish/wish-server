from db_helper import conn


def create_order_feedback(user_id: int, order_id: int, rate: int, text: str) -> None:
    """
    Создать запись в таблице обратной связи

    :param user_id: ID пользователя
    :param order_id: ID заказа
    :param rate: Оценка
    :param text: Текст обратной связи
    """

    cur = conn.cursor()
    cur.execute("INSERT INTO order_feedback (user_id, order_id, rate, text) VALUES (%s, %s, %s, %s)", (user_id, order_id, rate, text))
    conn.commit()
    cur.close()

def has_user_feedback(user_id: int, order_id: int) -> bool:
    """
    Проверить, оставил ли пользователь отзыв на конкретный заказ

    :param user_id: ID пользователя
    :param order_id: ID заказа
    :return: True, если отзыв оставлен, False иначе
    """

    cur = conn.cursor()
    cur.execute("SELECT id FROM order_feedback WHERE user_id = %s AND order_id = %s", (user_id, order_id))
    data = cur.fetchone()
    cur.close()

    return data is not None
