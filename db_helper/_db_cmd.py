import psycopg2
from . import conn_credentials


def commit(query: str, data: tuple = None) -> None:
    conn = psycopg2.connect(**conn_credentials)
    try:
        cur = conn.cursor()
        cur.execute(query, data)
        conn.commit()
    finally:
        cur.close()
        conn.close()


def fetchone(query: str, data: tuple = None) -> tuple:
    conn = psycopg2.connect(**conn_credentials)
    try:
        cur = conn.cursor()
        cur.execute(query, data)
        res = cur.fetchone()
    finally:
        cur.close()
        conn.close()
    return res


def fetchall(query: str, data: tuple = None) -> list[tuple]:
    conn = psycopg2.connect(**conn_credentials)
    try:
        cur = conn.cursor()
        cur.execute(query, data)
        res = cur.fetchall()
    finally:
        cur.close()
        conn.close()
    return res
