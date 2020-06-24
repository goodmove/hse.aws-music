import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
library_table = dynamodb.Table('library')
user_feed_table = dynamodb.Table('user_feed')


def lambda_handler(event, context):
    try:
        track_id = event['queryStringParameters']['track_id']
        user_id = event['queryStringParameters']['user_id']

        track = library_table.get_item(Key={"id": track_id})["Item"]

        try:
            user_feed_table.get_item(Key={'id': user_id})["Item"]
        except:
            user_feed_table.put_item(Item={'id': user_id, 'tracks': []})

        user_library = user_feed_table.get_item(Key={'id': user_id})["Item"]
        if track_id not in list(user_library["tracks"]):
            user_feed_table.update_item(
                Key={'id': user_id},
                UpdateExpression="SET tracks = list_append(tracks, :t)",
                ExpressionAttributeValues={
                    ':t': [track_id],
                },
                ReturnValues="UPDATED_NEW"
            )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Ok'})
        }
    except Exception as e:
        logger.error(e)
        response = {'message': 'Not found'}
        return {
            'statusCode': 404,
            'body': json.dumps(response)
        }
