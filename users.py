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


class CreateUserView(Resource):
    def post(self):
        try:
            data = request.get_json()
            if is_correct_url(data["site_address"]):
                email = data["email"]
                site_address = data["site_address"]
                access_token = create_access_token(identity=email, expires_delta=False)
                cnx = init_connection_db()
                cursor = cnx.cursor()
                cursor.execute(
                    "INSERT INTO rtwa_db.users" "(email, access_token, site_address)" "VALUES(%s, %s, %s)",
                    (
                        email,
                        access_token,
                        site_address,
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
                if not does_exists:
                    cursor.execute(
                        "INSERT INTO rtwa_db.sites" "(site_address)" "VALUES(%s)",
                        (
                            site_address,
                        )
                    )
                
                cursor.execute(
                    "SELECT id_users FROM rtwa_db.users WHERE access_token=%s",
                    (
                        access_token,
                    )
                )
                user_id = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT id_sites FROM rtwa_db.sites WHERE site_address=%s",
                    (
                        site_address,
                    )
                )
                site_id = cursor.fetchone()[0]

                cursor.execute(
                        "INSERT INTO rtwa_db.users_sites" "(id_users, id_sites)" "VALUES(%s, %s)",
                        (
                            user_id,
                            site_id,
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
        

class CreateEntryView(Resource):
    def post(self):
        try:
            data = request.get_json()
            page_url = data["page_url"] 
            ua_header = data["user_agent_header_value"]
            r_header = data["referer_header_value"]
            window_width = data["window_inner_width"]
            window_height = data["window_inner_height"]
            max_touchpoints = data["navigator_max_touchpoints"]
            language = data["navigator_language"]

            cnx = init_connection_db()
            cursor = cnx.cursor()
            cursor.execute(
                "SELECT id_sites FROM rtwa_db.sites WHERE site_address=%s",
                (
                    page_url,
                )
            )
            site_id = cursor.fetchone()
            does_exist = cursor.rowcount
            if not does_exist:
                cursor.close()
                cnx.close()
                return jsonify({"msg":"Data ignored, site not registered for tracking!"})
            else:
                cursor.execute(
                    "INSERT INTO rtwa_db.entries (id_site, ua_header, referer_header, language, max_touchpoints, window_height, window_width) VALUES(%s,%s,%s,%s,%s,%s, %s)",
                    (
                        site_id[0],
                        ua_header,
                        r_header,
                        language,
                        max_touchpoints,
                        window_height,
                        window_width,
                    )
                )
                cnx.commit()
                cursor.close()
                cnx.close()
                return jsonify({"msg":"success, data posted to db!"})
        
        except Exception as e:
            return jsonify({"msg":"something went wrong!", "error":str(e)})
        

class ListUsersSitesStatView(Resource):
    @jwt_required(locations="headers", refresh=False)
    def get(self):
        try:    
            user_identity = get_jwt_identity()
            cnx = init_connection_db()
            cursor = cnx.cursor()

            # rest of the code

            cnx.commit()
            cursor.close()
            cnx.close()
            return jsonify({"user":user_identity})
        except Exception as e:
            return jsonify({"msg":"something went wrong!", "error":str(e)})
