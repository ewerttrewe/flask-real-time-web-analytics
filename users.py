# app imports
from .utils import (
    is_correct_url,
    init_connection_db,
    create_schema_and_tables,
)

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
from redis.exceptions import ConnectionError, TimeoutError
from redis.retry import Retry
from redis.backoff import ExponentialBackoff

# connecting to redis
redis = Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    decode_responses=True,
    health_check_interval=5,
    retry=Retry(ExponentialBackoff(cap=10, base=1), 25),
    retry_on_error=[ConnectionError, TimeoutError, ConnectionResetError],
)
# loading env variables
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

                # hashed_keys = redis.keys("*")
                # for hk in hashed_keys:
                #     if redis.hget(f"{hk}", "domain") == page_url:
                #         redis.delete(f"{hk}")
                #         print(f"Cached value of the key:{hk} changed, key deleted!")

                hashed_keys = redis.keys("user:*")
                for k in hashed_keys:
                    if redis.json().get(f"{k}", "$")[0][1]["domain"] == page_url:
                        redis.delete(f"{k}")
                        print(f"Cached value of the key:{k} changed, key deleted!")

                return jsonify({"msg": "success, data posted to db!"})

        except Exception as e:
            return jsonify({"msg": "something went wrong!", "error": str(e)})


class ListUsersSitesStatView(Resource):
    @jwt_required(locations="headers", refresh=False)
    def get(self):
        try:
            user_identity = get_jwt_identity()

            # if redis.keys(f"user:{user_identity}"):
            #     results = redis.hget(f"user:{user_identity}", "results")
            #     print("Getting data from cache!...")
            #     return jsonify({"user": user_identity, "result": (results)})

            if redis.keys(f"user:{user_identity}"):
                results = redis.json().get(f"user:{user_identity}", "$")[0][0][
                    "results"
                ]
                # print(results)
                print("Loading data from cache!")
                return jsonify({"user": user_identity, "results": results})

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
                if not results:
                    return jsonify(
                        {"msg": "You have no entries on your site currently!"}
                    )
                # redis.hset(
                #     f"user:{user_identity}",
                #     mapping={"domain": f"{site_address}", "results": f"{results}"},
                # )

                redis.json().set(
                    f"user:{user_identity}",
                    "$",
                    [{"results": results}, {"domain": site_address}],
                )
                print("Saving data to cache!")
                cnx.commit()
                cursor.close()
                cnx.close()

                return jsonify({"user": user_identity, "results": results})
        except Exception as e:
            return jsonify({"msg": "something went wrong!", "error": str(e)})
