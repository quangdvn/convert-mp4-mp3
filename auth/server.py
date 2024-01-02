import os

import jwt
import psycopg2
from flask import Flask, request

from utils import create_jwt

# from flask_mysqldb import MySQL
server = Flask(__name__)

# Config
# server.config["POSTGRESQL_HOST"] = "localhost"
# server.config["POSTGRESQL_USER"] = "admin"
# server.config["POSTGRESQL_PASSWORD"] = "postgres"
# server.config["POSTGRESQL_PORT"] = "5432"
# server.config["POSTGRESQL_DB"] = "convert_auth"

db_connection = psycopg2.connect(
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    host=os.environ.get('DB_HOST'),
    port=os.environ.get('DB_PORT'),
    database=os.environ.get('DB_NAME')
)


@server.route("/", methods=["GET"])
def hello_gateway():
    # cur = db_connection.cursor()
    # res = cur.execute(
    #     "SELECT email, password FROM user"
    # )
    # if res > 0:
    #     user_row = cur.fetchone()
    #     print('1, ', user_row)
    #     email = user_row[0]  # type: ignore
    #     password = user_row[1]  # type: ignore
    #     return f"{email} and {password}", 200
    return "Hello World", 200


@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "Missing credentials", 401

    # Check DB for credentials
    cur = db_connection.cursor()
    res = cur.execute(
        "SELECT email, password FROM users WHERE email=%s", (auth.username,)
    )
    user_row = cur.fetchone()

    if user_row:
        print('1, ', user_row)
        email = user_row[0]  # type: ignore
        password = user_row[1]  # type: ignore

        if auth.username != email or auth.password != password:
            return 'Invalid credentials', 401

        return create_jwt(auth.username, os.environ.get('JWT_SECRET'), True)

    return 'Invalid credentials', 401


@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]
    if not encoded_jwt:
        return "Missing credentials", 401
    encoded_jwt = encoded_jwt.split(" ")[1]
    try:
        decoded = jwt.decode(
            encoded_jwt,
            os.environ.get('JWT_SECRET'),
            algorithms=["HS256"]
        )
    except:
        return "Not authorized", 403

    return decoded, 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5005)
