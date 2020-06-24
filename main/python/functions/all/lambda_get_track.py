import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
library_table = dynamodb.Table('library')


def lambda_handler(event, context):
    try:
        track_id = event['queryStringParameters']['track_id']
        track = library_table.get_item(Key={"id": track_id})["Item"]

        if track.get('vocabulary'):
            del track['vocabulary']

        return {
            'statusCode': 200,
            'body': json.dumps(track)
        }
    except Exception as e:
        logger.error(e)
        response = {'message': 'Not found'}
        return {
            'statusCode': 404,
            'body': json.dumps(response)
        }
