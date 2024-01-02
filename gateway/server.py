import json

import gridfs  # Store large files in MongoDB
import pika  # Inteface with RabbitMQ
from flask import Flask, request
from flask_pymongo import PyMongo  # Store video files in MongoDB

from auth_service import access
from authorization import validate
from storage import util

server = Flask(__name__)

server.config["MONGO_URI"] = "mongodb://admin:mongo@192.168.106.2:27017/videos?authSource=admin"

# Use to store files (mp3 - videos)
mongo = PyMongo(server)

RABBIT_MQ_SERVICE = 'convert-rabbitmq'

# Solve Mongo BSON Limits and Thresholds of 16MB per BSON document
# Seperate file into chunks (255kB) and metadata and store them in separate documents
# 1 collect - Chunks
# 1 collect - Metadatas
gridfs = gridfs.GridFS(mongo.db)

# Connect to RabbitMQ asynchronously
connection = pika.BlockingConnection(
    pika.ConnectionParameters(RABBIT_MQ_SERVICE)
)

# Gateway push Mess -> Queue -> Notify down-stream services about new video to consumer that mess
rabbit_channel = connection.channel()


@server.route("/", methods=["GET"])
def hello_gateway():
    return "Hello World!", 200


@server.route("/login", methods=["POST"])
def login():
    # Call to AUTH_SERVICE to login with username + password
    # and receive back the JWT token
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err


@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)
    server.logger.info("The real access:", access)
    access_info = json.loads(access)

    # "username"
    # "exp": datetime.datetime.utcnow(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
    # iat": datetime.datetime.utcnow(),
    # "admin": authz <- True
    if access_info["admin"]:
        # Allow one and only one file
        if len(request.files) > 1 or len(request.files) < 1:
            return "Exactly 1 file required", 400

        for _, file in request.files.items():
            err = util.upload(file, gridfs, rabbit_channel, access_info)

            if err:
                return err

        return "Success!", 200
    else:
        return "Not Authorized!", 401


@server.route("/download", methods=["GET"])
def download():
    pass


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
