#app imports
from .utils import is_correct_url, init_connection_db
#standard imports
from dotenv import load_dotenv
from requests import status_codes, Response
#3rd party imports
from flask_restful import Resource
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt
from flask import request
from flask import jsonify


load_dotenv()


class UsersRegistrationView(Resource):
    def post(self):
        # asigining data
        try:
            data = request.get_json()
            if is_correct_url(data["site_address"]):
                email = data["email"]
                site_address = data["site_address"]
                access_token = create_access_token(identity=email, expires_delta=False)
                #connecting to db
                cnx = init_connection_db()
                #opening cursor & executing query & commit to db
                cursor = cnx.cursor()
                cursor.execute(
                    "INSERT INTO rtwa_db.users" "(email, access_token)" "VALUES(%s, %s)",
                    (
                        email,
                        access_token
                    )
                )
                cursor.execute(
                    "SELECT site_address FROM rtwa_db.sites WHERE site_address=%s",
                    (
                        site_address,
                    )
                )
                cursor.fetchone()
                does_exists = cursor.rowcount
                print(does_exists)
                if not does_exists:
                
                    cursor.execute(
                        "INSERT INTO sites" "(site_address)" "VALUES(%s)",
                        (
                            site_address,
                        )
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
    def post(self):
        try:
            user_identity = get_jwt_identity()
            # cnx = init_connection_db()
            # cursor = cnx.cursor()

        

        # data = request.get_json()
        # page_url = data["page_url"] 
        # ua_header = data["user_agent_header_value"]
        # r_header = data["referer_header_value"]
        # window_inner_width = data["window_inner_width"]
        # window_inner_height = data["window_inner_height"]
        # nav_max_touch_points = data["navigator_max_touch_points"]
        # nav_language = data["navigator_language"]

            return jsonify({"msg":"success","user":user_identity})
        except Exception as e:
            return jsonify({"msg":"something went wrong!", "error":str(e)})