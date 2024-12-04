from api.v1 import api, check_auth
from flask import request
import db_helper
import phone_verification
import config


@api.route("/subscription/get-subscription-info")
def get_subscription_info():
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "message": "Unauthorized"}

    subscription = db_helper.subscription.get_user_subscription(user_id)
    if not subscription:
        return {"status": "ok", "subscription": None}

    users = []
    for user_id in subscription['family_members']:
        user = {"id": user_id}
        user_db = db_helper.user.get_user(user_id)
        user["phone"] = user_db['phone']
        user["name"] = user_db['name']
        users.append(user)
    subscription['family_members'] = users

    return {"status": "ok", "subscription": subscription}


@api.route("/subscription/send-invitation", methods=["POST"])
def subscription_send_invitation():
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "code": "unauthorized", "message": "Unauthorized"}
    
    phone = phone_verification.clean_phone(request.json["phone"])
    recipient = db_helper.user.get_user_by_phone(phone)
    if not recipient:
        return {"status": "error", "code": "user_not_found", "message": "User with this phone number does not exist"}
    
    # check if recipient is already in the family
    subscription = db_helper.subscription.get_user_subscription(recipient['id'])
    if subscription:
        if recipient['id'] == subscription['owner']:
            if subscription['is_active']:
                return {"status": "error", "code": "user_already_has_subscription", "message": "User is already has a subscription"}
        else:
            return {"status": "error", "code": "user_already_in_family", "message": "User is already in the family"}
    
    # check if user has already sent an invitation to this user
    other_invitations = db_helper.subscription.find_user_subscription_invitations(recipient['id'])
    if not all(invitation['owner'] != user_id for invitation in other_invitations):
        return {"status": "error", "code": "invitation_already_sent", "message": "Invitation to this user has already been sent"}
    
    # check if sum of family members + invitations is not greater than 3
    current_user_subscription = db_helper.subscription.get_user_subscription(user_id)
    family_members = current_user_subscription['family_members']
    invitations = db_helper.subscription.find_subscription_invitations_by_subscription_id(current_user_subscription['id'])
    if len(family_members) + len(invitations) >= config.MAX_FAMILY_MEMBERS:
        return {"status": "error", "code": "family_members_limit_reached", "message": "Family members limit reached"}
    
    db_helper.subscription.create_subscription_invitation(user_id, recipient['id'])
    return {"status": "ok"}


@api.route("/subscription/get-subscription-invitations")
def get_subscription_invitations():
    """
    Получить приглашения разных людей в конкретную подписку
    """
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "code": "unauthorized", "message": "Unauthorized"}

    subscription = db_helper.subscription.get_user_subscription(user_id)
    if not subscription:
        return {"status": "error", "code": "subscription_not_found", "message": "Subscription not found"}
    
    invitations = db_helper.subscription.find_subscription_invitations_by_subscription_id(subscription['id'])

    for invitation in invitations:
        user = db_helper.user.get_user(invitation['recipient'])
        invitation['recipient'] = {
            "id": invitation['recipient'],
            "phone": user['phone'],
            "name": user['name']
        }
    
    return {"status": "ok", "invitations": invitations}


@api.route("/subscription/get-user-invitations")
def get_user_subscription_invitations():
    """
    Получить приглашения текущего пользователя во все подписки
    """
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "code": "unauthorized", "message": "Unauthorized"}

    invitations = db_helper.subscription.find_user_subscription_invitations(user_id)

    for invitation in invitations:
        owner = db_helper.user.get_user(invitation['owner'])
        invitation['owner'] = {
            "id": invitation['owner'],
            "phone": owner['phone'],
            "name": owner['name']
        }
    
    return {"status": "ok", "invitations": invitations}


@api.route("/subscription/accept-invitation", methods=["POST"])
def subscription_accept_invitation():
    """
    Принять приглашение в подписку
    """
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "code": "unauthorized", "message": "Unauthorized"}

    invitation_id = request.json["invitation_id"]
    invitation = db_helper.subscription.get_subscription_invitation(invitation_id)
    if not invitation:
        return {"status": "error", "code": "invitation_not_found", "message": "Invitation not found"}

    # check if user is already in the family
    user_old_subscription = db_helper.subscription.get_user_subscription(user_id)
    if user_old_subscription:
        if user_old_subscription["owner"] == user_id:
            if user_old_subscription["is_active"]:
                return {"status": "error", "code": "already_has_subscription", "message": "User already has a subscription"}
            else:
                db_helper.subscription.delete_inactive_subscription(user_old_subscription["id"])
        else:
            return {"status": "error", "code": "already_in_family", "message": "User is already in the family"}

    db_helper.subscription.add_user_to_subscription_family(invitation['subscription_id'], user_id)
    db_helper.subscription.delete_subscription_invitation(invitation_id)
    return {"status": "ok"}


@api.route("/subscription/reject-invitation", methods=["POST"])
def subscription_reject_invitations():
    """
    Отклонить приглашение в подписку (пользователем, которого приглашают)
    """
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "code": "unauthorized", "message": "Unauthorized"}

    invitation_id = request.json["invitation_id"]
    invitation = db_helper.subscription.get_subscription_invitation(invitation_id)
    if not invitation:
        return {"status": "error", "code": "invitation_not_found", "message": "Invitation not found"}
    if invitation['recipient'] != user_id:
        return {"status": "error", "code": "not_invited_user", "message": "Not invited user"}
    
    db_helper.subscription.delete_subscription_invitation(invitation_id)

    return {"status": "ok"}


@api.route("/subscription/delete-invitation", methods=["POST"])
def subscription_delete_invitation():
    """
    Удалить приглашение в подписку (пользователем, который приглашает)
    """
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "code": "unauthorized", "message": "Unauthorized"}

    invitation_id = request.json["invitation_id"]
    invitation = db_helper.subscription.get_subscription_invitation(invitation_id)
    if not invitation:
        return {"status": "error", "code": "invitation_not_found", "message": "Invitation not found"}
    if invitation['owner'] != user_id:
        return {"status": "error", "code": "not_owner", "message": "Not owner"}

    db_helper.subscription.delete_subscription_invitation(invitation_id)

    return {"status": "ok"}
