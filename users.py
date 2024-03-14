from flask_restful import Resource
from flask import request
import mysql.connector


class UsersRegistrationView(Resource):
    def post(self):
        # asigining data
        data = request.get_json()
        email = data["email"]
        registered_site = data["registered_site"]
        password = data["password"]
        cnx = mysql.connector.connect(
            user="ewerttrewe",
            password="Ewert961124.",
            host="localhost",
            database="rtwa_users",
        )
        cursor = cnx.cursor(dictionary=True)
        query = "SELECT email FROM users"
        cursor.execute(query)
        cnx.commit()
        for row in cursor:
            if email == row["email"]:
                cursor.close()
                cnx.close()
                return f"Account with {email} address is already registered! Provide unique email address!"

            else:
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
