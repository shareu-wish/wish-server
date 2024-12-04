from api.v1 import api
from flask import request
import db_helper


@api.route("/landing-forms/support", methods=["POST"])
def support():
    """
    Поддержка    
    """
    name = request.json["name"]
    city = request.json["city"]
    email = request.json["email"]
    phone = request.json["phone"]
    text = request.json["text"]

    if not name or not city or not text:
        return {"status": "error", "message": "Заполните обязательные поля!"}
    
    db_helper.landing_forms.create_support_request(name, city, email, phone, text)

    return {"status": "ok"}


@api.route("/landing-forms/install-station-request", methods=["POST"])
def install_station_request():
    name = request.json["name"]
    organization = request.json["organization"]
    city = request.json["city"]
    email = request.json["email"]
    phone = request.json["phone"]
    text = request.json["text"]

    if not organization or not city:
        return {"status": "error", "message": "Заполните обязательные поля!"}
    
    db_helper.landing_forms.create_install_station_request(name, organization, city, email, phone, text)

    return {"status": "ok"}
