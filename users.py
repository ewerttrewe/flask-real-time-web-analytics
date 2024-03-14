from flask_restful import Resource
from flask import request

from .utils import is_correct_url

from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()


class UsersRegistrationView(Resource):
    def post(self):
        # asigining data
        try:
            data = request.get_json()
            if is_correct_url(data["registered_site"]):
                email = data["email"]
                registered_site = data["registered_site"]
                password = data["password"]
                cnx = mysql.connector.connect(
                    user=os.getenv("USER"),
                    password=os.getenv("PASSWORD"),
                    host=os.getenv("HOST"),
                    database=os.getenv("DATABASE"),
                )
                cursor = cnx.cursor()
                cursor.execute(
                    "INSERT INTO users" "(email, site, password)" "VALUES(%s, %s, %s)",
                    (
                        email,
                        registered_site,
                        password,
                    ),
                )
                cnx.commit()
                cursor.close()
                cnx.close()
                return "data posted to db"
            else:
                return "please provide correct url address"
        except:
            return "your address email must be unique!"
