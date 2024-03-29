#app imports
from .utils import is_correct_url
#standard imports
from dotenv import load_dotenv
import mysql.connector
import os
#3rd party imports
from flask_restful import Resource
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask import request
from flask import jsonify


load_dotenv()


class UsersRegistrationView(Resource):
    def post(self):
        # asigining data
        try:
            data = request.get_json()
            print(data)
            if is_correct_url(data["registered_site"]):
                email = data["email"]
                registered_site = data["registered_site"]
                
                #connecting to db
                cnx = mysql.connector.connect(
                    user=os.getenv("USER"),
                    password=os.getenv("PASSWORD"),
                    host=os.getenv("HOST"),
                    database=os.getenv("DATABASE"),
                )
                print(cnx.is_connected())
                #opening cursor & executing query & commit to db
                cursor = cnx.cursor()
                cursor.execute(
                    "INSERT INTO users" "(email, registered_site)" "VALUES(%s, %s)",
                    (
                        email,
                        registered_site,
                    ),
                )
                cnx.commit()
                cursor.close()
                cnx.close()
                return "data posted to db" 
            else:
                return "please provide correct url address"
        except Exception as e:
            return jsonify({"something went wrong!":str(e)})
