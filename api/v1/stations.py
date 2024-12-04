from api.v1 import api
import db_helper


@api.route("/stations/get-all-stations")
def get_all_stations():
    """
    Возвращает все станции со всеми данными
    """
    return db_helper.stations.get_stations()

