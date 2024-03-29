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
            if is_correct_url(data["registered_site"]):
                email = data["email"]
                registered_site = data["registered_site"]
                access_token = create_access_token(identity=email, expires_delta=False)
                #connecting to db
                cnx = mysql.connector.connect(
                    user=os.getenv("USER"),
                    password=os.getenv("PASSWORD"),
                    host=os.getenv("HOST"),
                    database=os.getenv("DATABASE"),
                )
                #opening cursor & executing query & commit to db
                cursor = cnx.cursor()
                cursor.execute(
                    "INSERT INTO users" "(email, registered_site, access_token)" "VALUES(%s, %s, %s)",
                    (
                        email,
                        registered_site,
                        access_token
                    ),
                )
                cnx.commit()
                cursor.close()
                cnx.close()
                return jsonify({"msg":"data posted to db", "access_token":access_token}) 
            else:
                return "please provide correct url address"
        except Exception as e:
            return jsonify({"msg":"something went wrong!", "error":str(e)})
        

class UserProtectedView(Resource):
    @jwt_required(locations="headers", refresh=False)
    def get(self):
        user_identity = get_jwt_identity()

        return jsonify({"msg":"success","user":user_identity})