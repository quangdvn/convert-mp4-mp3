import json

import pika


def upload(file, gridfs, rabbit_channel, access_info):
    try:
        file_id = gridfs.put(file)
    except Exception as err:
        print("GridFS put file error: ", err)
        return f"Internal Server Error with GridFS: {err}", 500

    mess = {
        "video_file_id": str(file_id),
        "mp3_file_id": None,
        "username": access_info["username"]
    }

    try:
        rabbit_channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(mess),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
    except Exception as err:
        print("Error while publish message: ", err)
        gridfs.delete(file_id)
        return f"Internal Server Error with RabbitMQ: {err}", 500
