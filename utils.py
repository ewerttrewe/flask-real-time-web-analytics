import re
import mysql.connector
import os
from mysql.connector import Error


def is_correct_url(user_url):
    reg = r"^(?:http|https):\/\/(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?$"
    is_url = bool(re.search(reg, user_url))
    return is_url


def init_connection_db():
    try:
        connection_to_db = mysql.connector.connect(
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_ROOT_PASSWORD"),
            host=os.getenv("MYSQL_HOST"),
            # database=os.getenv("MYSQL_DATABASE"),
        )
        if connection_to_db.is_connected():
            print("MySQL connection established.")
            return connection_to_db
    except Error as e:
        return "Cannot connect to db!", e


def create_schema_and_tables(cnx):
    try:
        print(cnx)
        cursor = cnx.cursor()

        # Create schema
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS {}".format(os.getenv("MYSQL_DATABASE"))
        )

        # Switch to the created database
        cursor.execute(
            "USE {}".format(os.getenv("MYSQL_DATABASE")),
        )

        # Create tables
        users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id_users INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                email VARCHAR(255) UNIQUE NOT NULL,
                access_token TEXT NOT NULL,
                site_address VARCHAR(255) NOT NULL
            )
        """

        sites_table = """
            CREATE TABLE IF NOT EXISTS sites (
                id_sites INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                site_address VARCHAR(255) NOT NULL
            )
        """

        users_sites_table = """
            CREATE TABLE IF NOT EXISTS users_sites (
                id_users_sites INT NOT NULL AUTO_INCREMENT,
                id_users INT NOT NULL,
                id_sites INT NOT NULL,
                PRIMARY KEY (id_users_sites),
                INDEX id_users_idx (id_users ASC),
                INDEX id_sites_idx (id_sites ASC),
                FOREIGN KEY (id_users) REFERENCES users (id_users)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
                FOREIGN KEY (id_sites) REFERENCES sites (id_sites)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            )
        """

        entries_table = """
            CREATE TABLE IF NOT EXISTS entries (
                id_entries INT NOT NULL AUTO_INCREMENT,
                id_site INT NOT NULL,
                page_url VARCHAR(255) NOT NULL,
                ua_header VARCHAR(255) NOT NULL,
                referer_header VARCHAR(255) NOT NULL,
                language VARCHAR(255) NOT NULL,
                max_touchpoints INT NOT NULL,
                window_height INT NOT NULL,
                window_width INT NOT NULL,
                posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                PRIMARY KEY (id_entries),
                FOREIGN KEY (id_site) REFERENCES sites (id_sites)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            )
        """
        cursor.execute(users_table)
        cursor.execute(sites_table)
        cursor.execute(users_sites_table)
        cursor.execute(entries_table)
        cnx.commit()
        print("Setting up database successfull!.")
        return cursor
    except Error as e:
        print(f"Error creating schema and tables: {e}")
