import requests
import json
import boto3
import uuid

API_ENDPOINT = "https://orion.apiseeds.com/api/music/lyric"
API_KEY = "xyOkzMouRA2IMy56NgBk27mXK4leAXrIAGYSOTS8EIgCaU3gl34faWO3cqQWm8Qt"
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
sqs = boto3.resource('sqs', region_name='us-east-1')
library_table = dynamodb.Table('library')
indexing_queue = sqs.get_queue_by_name(QueueName='track-indexing')


def download_lyrics(artist_name, track_name):
    url = API_ENDPOINT + "/" + artist_name + "/" + track_name + "?apikey=" + API_KEY
    print(url)
    content = requests.get(url).json()

    print(content)
    if content.get("error") is not None:
        return None

    result = content["result"]
    if result["track"]["lang"]["code"] != "en":
        return None

    return {
        "artist": result["artist"]["name"],
        "track": result["track"]["name"],
        "lyrics": result["track"]["text"],
    }


def save_track_to_db(track_info):
    track_info["id"] = str(uuid.uuid4())

    with library_table.batch_writer() as batch:
        library_table.put_item(Item=track_info)

    return track_info


def send_to_queue(track_id):
    indexing_queue.send_message(
        MessageBody=json.dumps({"track_id": track_id})
    )


def lambda_handler(event, context):
    in_artist_name = None
    in_track_name = None

    if event.get("queryStringParameters") is not None:
        in_artist_name = event["queryStringParameters"]["artist"]
        in_track_name = event["queryStringParameters"]["track"]
    else:
        in_artist_name = event["artist"]
        in_track_name = event["track"]

    track_info = download_lyrics(in_artist_name, in_track_name)

    if track_info is not None:
        save_track_to_db(track_info)
        send_to_queue(track_info["id"])

    response = {
        "track_info": track_info
    }
    return {
        "statusCode": 200,
        "body": json.dumps(response)
    }
