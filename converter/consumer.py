import os
import sys

import gridfs
import pika
from pymongo import MongoClient

from convert import to_mp3

RABBIT_MQ_SERVICE = "convert-rabbitmq"


def main():
    print("Waiting for mess...")
    mongo_client = MongoClient("mongodb://admin:mongo@192.168.106.2:27017/")
    db_videos = mongo_client.videos
    db_mp3s = mongo_client.mp3s

    # GridFS MongoDB
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    # RabbitMQ Connection
    rabbit_connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBIT_MQ_SERVICE)
    )
    channel = rabbit_connection.channel()

    def consume_callback(channel, method, properties, body):
        # Convert video into mp3 file
        err = to_mp3.start(body, fs_videos, fs_mp3s, channel)
        if err:
            # Negative Acknowledgement -> Mess won't be removed if failure occurs
            channel.basic_nack(delivery_tag=method.delivery_tag)
        else:
            # Acknowledgement the message if video is successfully converted
            channel.basic_ack(delivery_tag=method.delivery_tag)

    # Receive a messsage -> Consume the message -> Store mp3 output to MongoDB
    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=consume_callback
    )

    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except:
            os._exit(0)
