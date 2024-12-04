import psycopg2
import config


conn = psycopg2.connect(
    dbname=config.DB_NAME,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
)


from . import auth
from . import user
from . import stations
from . import orders
from . import station_controller
from . import payments
from . import landing_forms
from . import order_feedback
from . import subscription
