import json
import random
from lib_language import build_vocab_from_text

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
library_table = dynamodb.Table('library')
user_dictionary_table = dynamodb.Table('user_dictionary')
user_library_table = dynamodb.Table('user_library')


def word_comparator(word):
    return 1


def lambda_handler(event, context):
    user_id = event['queryStringParameters']['user_id']
    user_tracks = user_library_table.get_item(Key={'id': user_id})["Item"].get("tracks", [])
    user_words = set(user_dictionary_table.get_item(Key={'id': user_id})["Item"].get("words", []))

    indices = list(range(len(user_tracks)))
    random.shuffle(indices)

    found = False
    suggested_word = None
    suggested_song = None

    while not found and len(indices) > 0:
        track_id = indices.pop()
        track = library_table.get_item(Key={'id': track_id})["Item"]
        track_vocabulary = track['vocabulary']['eng']
        track_words = set(track_vocabulary.keys())

        unknown_words = track_words - user_words

        if len(unknown_words) > 0:
            unknown_words = sorted(list(unknown_words), key=word_comparator, reverse=True)
            suggested_word = unknown_words[0]
            suggested_song = track_id
            found = True

    if not found:
        return {
            'statusCode': 500,
            'body': 'New words are not available at the moment'
        }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'word': suggested_word,
            'track_id': suggested_song
        })
    }
