from db_helper import conn
from datetime import datetime
import datetime as dt


def get_user_subscription(user_id: int) -> dict | None:
    """
    Получить подписку пользователя

    :param user_id: ID пользователя
    :return: dict с данными о подписке\n
        - *id*: ID подписки
        - *owner*: ID пользователя, оплачивающего подписку
        - *family_members*: ID пользователей членов семьи
        - *until*: Дата и время, до которых действует подписка
        - *is_active*: Действует ли сейчас подписка
    """

    cur = conn.cursor()
    # Find subscription where user_id in family_members array
    cur.execute("SELECT id, owner, family_members, until FROM subscriptions WHERE %s = ANY(family_members)", (user_id,))
    data = cur.fetchone()
    cur.close()

    if data is None:
        return None

    res = {
        "id": data[0],
        "owner": data[1],
        "family_members": data[2],
        "until": data[3],
        "is_active": data[3] > datetime.now().astimezone(tz=dt.timezone(dt.timedelta(seconds=10800)))
    }

    return res


def get_subscription(subscription_id: int) -> dict | None:
    """
    Получить подписку по ID

    :param subscription_id: ID подписки
    :return: dict с данными о подписке\n
        - *owner*: ID пользователя, оплачивающего подписку
        - *family_members*: ID пользователей членов семьи
        - *until*: Дата и время, до которых действует подписка
        - *is_active*: Действует ли сейчас подписка
    """

    cur = conn.cursor()
    cur.execute("SELECT owner, family_members, until FROM subscriptions WHERE id = %s", (subscription_id,))
    data = cur.fetchone()
    cur.close()

    if data is None:
        return None

    res = {
        "owner": data[0],
        "family_members": data[1],
        "until": data[2],
        "is_active": data[2] > datetime.now().astimezone(tz=dt.timezone(dt.timedelta(seconds=10800)))
    }

    return res


def create_subscription_invitation(user_id: int, recipient_id: int) -> None:
    """
    Создать приглашение в подписку

    :param user_id: ID пользователя, который пригласил в свою подписку
    :param recipient_id: ID пользователя, который приглашается
    """

    # get subscription_id by user_id
    cur = conn.cursor()
    cur.execute("SELECT id FROM subscriptions WHERE owner = %s", (user_id,))
    data = cur.fetchone()
    cur.close()
    if data is None:
        return
    subscription_id = data[0]
    
    # insert data in subscription_invitations
    cur = conn.cursor()
    cur.execute("INSERT INTO subscription_invitations (subscription_id, owner, recipient) VALUES (%s, %s, %s)", (subscription_id, user_id, recipient_id))
    conn.commit()
    cur.close()


def get_subscription_invitation(invitation_id: int) -> dict | None:
    """
    Найти приглашение в подписку

    :param invitation_id: ID приглашения
    :return: dict с данными о приглашении\n
        - *id*: ID приглашения
        - *subscription_id*: ID подписки
        - *owner*: ID пользователя, который пригласил в свою подписку
        - *recipient*: ID пользователя, который приглашается
    """

    cur = conn.cursor()
    cur.execute("SELECT id, subscription_id, owner, recipient FROM subscription_invitations WHERE id = %s", (invitation_id, ))
    data = cur.fetchone()
    cur.close()

    if data is None:
        return None

    res = {
        "id": data[0],
        "subscription_id": data[1],
        "owner": data[2],
        "recipient": data[3]
    }

    return res


def find_user_subscription_invitations(user_id: int) -> list[dict]:
    """
    Найти приглашения в подписку

    :param user_id: ID пользователя, которого приглашают
    :return: Список приглашений в подписку\n
        - *id*: ID приглашения
        - *subscription_id*: ID подписки
        - *owner*: ID пользователя, который пригласил в свою подписку
        - *recipient*: ID пользователя, который приглашается
    """

    cur = conn.cursor()
    cur.execute("SELECT id, subscription_id, owner, recipient FROM subscription_invitations WHERE recipient = %s", (user_id,))
    data = cur.fetchall()
    cur.close()

    res = []
    for invitation in data:
        res.append({
            "id": invitation[0],
            "subscription_id": invitation[1],
            "owner": invitation[2],
            "recipient": invitation[3]
        })

    return res


def find_subscription_invitations_by_subscription_id(subscription_id: int) -> list[dict]:
    """
    Найти приглашения в подписку

    :param subscription_id: ID подписки
    :return: Список приглашений в подписку\n
        - *id*: ID приглашения
        - *owner*: ID пользователя, который пригласил в свою подписку
        - *recipient*: ID пользователя, который приглашается
    """

    cur = conn.cursor()
    cur.execute("SELECT id, owner, recipient FROM subscription_invitations WHERE subscription_id = %s", (subscription_id,))
    data = cur.fetchall()
    cur.close()

    res = []
    for invitation in data:
        res.append({
            "id": invitation[0],
            "owner": invitation[1],
            "recipient": invitation[2]
        })

    return res


def delete_subscription_invitation(invitation_id: int) -> None:
    """
    Удалить приглашение в подписку

    :param invitation_id: ID приглашения
    """

    cur = conn.cursor()
    cur.execute("DELETE FROM subscription_invitations WHERE id = %s", (invitation_id, ))
    conn.commit()
    cur.close()


def delete_inactive_subscription(subscription_id: int) -> None:
    """
    Удалить неактивную подписку

    :param subscription_id: ID подписки
    """

    cur = conn.cursor()
    cur.execute("DELETE FROM subscriptions WHERE id = %s AND until < %s", (subscription_id, datetime.now().astimezone(tz=dt.timezone(dt.timedelta(seconds=10800)))))
    conn.commit()
    cur.close()


def add_user_to_subscription_family(subscription_id: int, user_id: int) -> None:
    """
    Добавить пользователя в семью подписки

    :param subscription_id: ID подписки
    :param user_id: ID пользователя
    """

    cur = conn.cursor()
    cur.execute("UPDATE subscriptions SET family_members = array_append(family_members, %s) WHERE id = %s", (user_id, subscription_id))
    conn.commit()
    cur.close()
