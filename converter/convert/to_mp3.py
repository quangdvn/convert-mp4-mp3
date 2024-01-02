import json
import os
import tempfile

import moviepy.editor
import pika
from bson.objectid import ObjectId

# def start(message, fs_videos, fs_mp3s, channel):
#     # Deserialize string -> Python object
#     print("Message received from RabbitMQ: ", message)
#     json_messsage = json.loads(message)

#     # Empty temp file
#     temp_file = tempfile.NamedTemporaryFile()

#     # Video contents - Convert video_file_id to MongoDB ObjectId
#     out = fs_videos.get(ObjectId(json_messsage['video_file_id']))

#     # Add video contents to empty file
#     temp_file.write(out.read())

#     # Create audio from temp video file
#     audio = moviepy.editor.VideoFileClip(temp_file.name).subclip(0, 10).audio
#     temp_file.close()

#     # Write audio to the file
#     tf_path = tempfile.gettempdir() + f"/{json_messsage['vide_file_id']}.mp3"
#     audio.write_audiofile(tf_path)

#     # Save file to Mongo
#     # with open(tf_path, 'rb') as file:
#     #     data = file.read()
#     #     file_id = fs_mp3s.put(data)
#     #     file.close()
#     #     os.remove(tf_path)
#     file = open(tf_path, "rb")
#     data = file.read()
#     file_id = fs_mp3s.put(data)
#     file.close()
#     os.remove(tf_path)

#     json_messsage['mp3_file_id'] = str(file_id)
#     print("Data to be put back into RabbitMQ: ", json_messsage)
#     try:
#         channel.basic_publish(
#             exchange="",
#             routing_key=os.environ.get("MP3_QUEUE"),
#             body=json.dumps(json_messsage),
#             properties=pika.BasicProperties(
#                 delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE  # Persist until processed
#             )
#         )
#     except Exception as err:
#         # Delete mp3 file from MongoDB if mess not added to the RabbitMQ queue
#         fs_mp3s.delete(file_id)
#         return "Failed to publish message"


def start(message, fs_videos, fs_mp3s, channel):
    try:
        # Deserialize string -> Python object
        print("Message received from RabbitMQ: ", message)
        json_message = json.loads(message)

        # Process video and extract audio
        audio_file_path = process_video_and_extract_audio(
            json_message, fs_videos)

        # Save audio file to MongoDB using GridFS
        audio_file_id = save_audio_to_mongodb(audio_file_path, fs_mp3s)

        # Update message and republish to RabbitMQ
        json_message['mp3_file_id'] = str(audio_file_id)
        republish_message(json_message, channel)

    except Exception as err:
        print(f"An error occurred: {err}")
        # Handle specific cleanup or error logging if needed
        return "Failed to process message"


def process_video_and_extract_audio(json_message, fs_videos):
    video_file_id = ObjectId(json_message['video_file_id'])
    with tempfile.NamedTemporaryFile(suffix=".mp4") as temp_video_file:
        # Retrieve video content from GridFS
        out = fs_videos.get(video_file_id)
        temp_video_file.write(out.read())
        temp_video_file.flush()

        # Extract audio from video
        audio = moviepy.editor.VideoFileClip(
            temp_video_file.name).subclip(0, 10).audio

    # Write audio to a temporary file
    temp_audio_path = tempfile.mktemp(suffix=".mp3")
    audio.write_audiofile(temp_audio_path)

    return temp_audio_path


def save_audio_to_mongodb(audio_file_path, fs_mp3s):
    with open(audio_file_path, 'rb') as audio_file:
        file_id = fs_mp3s.put(audio_file)

    os.remove(audio_file_path)  # Clean up the temporary audio file
    return file_id


def republish_message(json_message, channel):
    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(json_message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE  # Persist until processed
            )
        )
    except Exception as err:
        print(f"Failed to publish message to RabbitMQ: {err}")
        raise
