import pymysql
from pymysql.cursors import DictCursor

DB_CONFIG = {
    "host": "192.168.1.185",
    "user": "root",
    "password": "Wzh010310",
    "database": "zhaopin",
    "charset": "utf8mb4"

}

def connect_db():
    return pymysql.connect(**DB_CONFIG, cursorclass=DictCursor)
