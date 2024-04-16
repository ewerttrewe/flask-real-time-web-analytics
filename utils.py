import re
import mysql.connector
import os


def is_correct_url(user_url):
    reg = r"^(?:http|https):\/\/(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?$"
    is_url = bool(re.search(reg, user_url))
    return is_url


def init_connection_db():
    connection_to_db = mysql.connector.connect(
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        host=os.getenv("HOST"),
        database=os.getenv("DATABASE"),
    )
    return connection_to_db
