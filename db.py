import pymysql
from pymysql.cursors import DictCursor

DB_CONFIG = {
    "host": "jq777.cn",
    "user": "root",
    "password": "Wzh010310",
    "database": "zhaopin",

    "charset": "utf8mb4"

}

def connect_db():
    return pymysql.connect(**DB_CONFIG, cursorclass=DictCursor)
