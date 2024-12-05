from flask import Flask, send_from_directory
import config
from waitress import serve
from api.v1 import api as api_v1
from flask_swagger_ui import get_swaggerui_blueprint


app = Flask(__name__)

# Подключение API файлов
app.register_blueprint(api_v1, url_prefix='/v1/')


# Swagger UI
@app.route('/dev/docs_v1.yaml')
def get_swagger_file():
    return send_from_directory("api", "docs_v1.yaml")

SWAGGER_URL = "/dev/docs/v1"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, # URL для доступа к Swagger UI
    "/dev/docs_v1.yaml", # Путь к YAML файлу (URL)
    config={
        "app_name": "WISH"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


# Главная страница
@app.route("/")
def index():
    return {"text": "Привет 😉!"}


if __name__ == "__main__":
    if config.DEBUG:
        app.run(port=5050, debug=True, host=config.DEBUG_HOST, use_reloader=False)
    else:
        serve(app, host=config.HOST, port=config.PORT, url_scheme="https", threads=100)
