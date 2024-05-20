# app imports
from .utils import is_correct_url, init_connection_db, create_schema_and_tables


# standard imports
from dotenv import load_dotenv
import os
import json

# 3rd party imports
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from flask import request
from flask import jsonify
from redis import Redis

load_dotenv()


redis = Redis(
    host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True
)


class HelloWorld(Resource):
    def get(self):
        try:
            redis.ping()
            redis.set("imie", "maciek")
            print("success, redis connected!, random key created")
        except Exception as e:
            print(f"Error connecting to redis: {e}")

        redis.incr("hits")
        counter = str(redis.get("hits"), "utf-8")
        ki = str(redis.get("imie"), "utf-8")
        return (
            "Welcome to this webapage!, This webpage has been viewed "
            + counter
            + " time(s)"
            + ki
        )


class CreateUserView(Resource):
    def post(self):
        try:
            data = request.get_json()
            if is_correct_url(data["site_address"]):
                email = data["email"]
                site_address = data["site_address"]
                access_token = create_access_token(identity=email, expires_delta=False)

                cnx = init_connection_db()

                create_schema_and_tables(cnx)

                cursor = cnx.cursor()
                cursor.execute(
                    "INSERT INTO rtwa_users.users"
                    "(email, access_token, site_address)"
                    "VALUES(%s, %s, %s)",
                    (
                        email,
                        access_token,
                        site_address,
                    ),
                )

                cursor.execute(
                    "SELECT site_address FROM rtwa_users.sites WHERE site_address=%s",
                    (site_address,),
                )
                cursor.fetchone()

                does_exists = cursor.rowcount
                if not does_exists:
                    cursor.execute(
                        "INSERT INTO rtwa_users.sites" "(site_address)" "VALUES(%s)",
                        (site_address,),
                    )

                cursor.execute(
                    "SELECT id_users FROM rtwa_users.users WHERE access_token=%s",
                    (access_token,),
                )
                user_id = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT id_sites FROM rtwa_users.sites WHERE site_address=%s",
                    (site_address,),
                )
                site_id = cursor.fetchone()[0]

                cursor.execute(
                    "INSERT INTO rtwa_users.users_sites"
                    "(id_users, id_sites)"
                    "VALUES(%s, %s)",
                    (
                        user_id,
                        site_id,
                    ),
                )
                cnx.commit()
                cursor.close()
                cnx.close()
                return jsonify(
                    {"msg": "data posted to db", "access_token": access_token}
                )
            else:
                return "please provide correct url address"
        except Exception as e:
            return jsonify({"msg": "something went wrong!", "error": str(e)})


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
                "SELECT id_sites FROM rtwa_users.sites WHERE site_address=%s",
                (page_url,),
            )
            site_id = cursor.fetchone()
            does_exist = cursor.rowcount
            if not does_exist:
                cursor.close()
                cnx.close()
                return jsonify(
                    {"msg": "Data ignored, site not registered for tracking!"}
                )
            else:
                cursor.execute(
                    "INSERT INTO rtwa_users.entries (id_site, page_url, ua_header, referer_header, language, max_touchpoints, window_height, window_width) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        site_id[0],
                        page_url,
                        ua_header,
                        r_header,
                        language,
                        max_touchpoints,
                        window_height,
                        window_width,
                    ),
                )
                cnx.commit()
                cursor.close()
                cnx.close()
                return jsonify({"msg": "success, data posted to db!"})

        except Exception as e:
            return jsonify({"msg": "something went wrong!", "error": str(e)})


class ListUsersSitesStatView(Resource):
    @jwt_required(locations="headers", refresh=False)
    def get(self):
        try:
            user_identity = get_jwt_identity()
            if redis.keys(f"{user_identity}"):
                results = redis.json().get(f"{user_identity}", "$")
                print("Loading data from cache!...")
                return jsonify({"user": user_identity, "result": (results)})

            else:
                cnx = init_connection_db()
                cursor = cnx.cursor(dictionary=True)
                cursor.execute(
                    "SELECT site_address FROM rtwa_users.users WHERE email=%s",
                    (user_identity,),
                )
                site_address = cursor.fetchone()["site_address"]
                cursor.execute(
                    "SELECT s.site_address, e.page_url, e.ua_header, e.referer_header FROM rtwa_users.sites AS s INNER JOIN rtwa_users.entries AS e ON s.id_sites = e.id_site WHERE s.site_address =%s",
                    (site_address,),
                )
                results = cursor.fetchall()
                redis.json().set(user_identity, "$", results)
                print("Data cached to redis!")
                cnx.commit()
                cursor.close()
                cnx.close()

                return jsonify({"user": user_identity, "result": results})
        except Exception as e:
            return jsonify({"msg": "something went wrong!", "error": str(e)})
