import json
import boto3
import logging
from lib_language import build_vocab_from_text

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
library_table = dynamodb.Table('library')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def main_handler(track_id):
    logger.info('Starting indexing. track_id=' + track_id)

    try:
        track = library_table.get_item(Key={"id": track_id})["Item"]
        vocab = build_vocab_from_text(track["lyrics"])
        library_table.update_item(
            Key={"id": track_id},
            UpdateExpression="set vocabulary = :ve",
            ExpressionAttributeValues={
                ':ve': {"eng": vocab}
            },
        )
    except Exception as e:
        logger.error('Error during track indexing', e)
        raise e

    logger.info('Finished indexing')


def process_records(records):
    logger.info('Received records for indexing')
    if len(records) == 0:
        logger.info('Empty records set – aborting')
        return

    try:
        record_body = json.loads(records[0]["body"])
        main_handler(record_body["track_id"])
    except Exception as e:
        pass


def process_manually(track_id):
    logger.info('Received track id for manual indexing')
    main_handler(track_id)


def lambda_handler(event, context):
    if event.get('Records'):
        process_records(event["Records"])

    if event.get('queryStringParameters'):
        response = None
        track_id = event['queryStringParameters']['track_id']
        try:
            process_manually(track_id)
            response = {'indexing': 'Ok', 'track_id': track_id}
        except Exception as e:
            response = {'indexing': 'Failed', 'track_id': track_id}

        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
