import json
import requests
import os
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import datetime

SENTIMENT_FIELDS = ["Mixed", "Negative", "Neutral", "Positive"]

FACTOR = 0.7

def lambda_handler(event, context):
    cat_token, bot_token, open_conversation_url, get_cat_url, post_message_url = load_vars()
    body = json.loads(event['body'])
    # print(event)
    # print(context)
    if body['type'] == "url_verification":
        return {
            'statusCode': 200,
            'body': json.dumps({"challenge": body["challenge"]})
        }
    elif body['event']['type'] == "message":
        dynamodb = boto3.resource('dynamodb')
        sentiment_table = dynamodb.Table('slack-sentiment-records')
        userid = body['event']['user']
        entry = sentiment_table.get_item(Key={'userid': userid})
        print(entry)

        sentiment = query_comprehend(body)["SentimentScore"]
        timestamp = int(body['event']['ts'].split('.')[0])

        if ("Item" not in entry):
            print("does not have Item for user ", userid)
            aggregate = {
                "Mixed": Decimal(str(sentiment["Mixed"])),
                "Negative": Decimal(str(sentiment["Negative"])),
                "Neutral": Decimal(str(sentiment["Neutral"])),
                "Positive": Decimal(str(sentiment["Positive"]))
            }
            channel_id = get_channel(userid, bot_token, open_conversation_url)  # async?
            put_sentiment(userid, aggregate, timestamp, sentiment_table, channel_id)
        else:
            if ("kitty_channel_id" not in entry):
                channel_id = get_channel(userid, bot_token, open_conversation_url)
            else:
                channel_id = entry['kitty_channel_id']

            aggregate = aggregate_sentiment(sentiment, timestamp, entry)
            put_sentiment(userid, aggregate, timestamp, sentiment_table, channel_id)

        if (should_send_kitty(aggregate)):
            send_random_cat(channel_id, cat_token, bot_token, get_cat_url, post_message_url)
    else:
        print(body)

    return {
        "statusCode": 200
    }

def query_comprehend(body):
    client = boto3.client('comprehend')
    print(body['event']['text'])
    sentiment = client.detect_sentiment(Text=body['event']['text'], LanguageCode='en')
    print("Current sentiment: ", sentiment)
    return sentiment


def aggregate_sentiment(sentiment, timestamp, entry):
    if ("timestamp" not in entry["Item"] or \
            "sentiment" not in entry["Item"]):
        print("does not have the correct timestamp or sentiment for user ", userid)
        return sentiment

    dcurrent = datetime.datetime.fromtimestamp(timestamp)
    dbefore = datetime.datetime.fromtimestamp(int(entry["Item"]["timestamp"]))
    timediff = dcurrent - dbefore

    hours = timediff.seconds // 3600

    if timediff.days > 0:
        frac = FACTOR / (hours + timediff.days * 24)
    elif (hours > 0):
        frac = FACTOR - (0.7 - 0.2 * hours / 23.0)
    else:
        frac = FACTOR

    prev_sentiment = entry["Item"]["sentiment"]

    result = {}
    for s in SENTIMENT_FIELDS:
        result[s] = Decimal(sentiment[s] * frac) + \
                    prev_sentiment[s] * Decimal(1.0 - frac)

    return result


def put_sentiment(userid, sentiment, timestamp, sentiment_table, channel_id=None):
    if channel_id:
        put_response = sentiment_table.put_item(Item={
            'userid': userid,
            'sentiment': sentiment,
            "timestamp": timestamp,
            'kitty_channel_id': channel_id
        })
    else:
        put_response = sentiment_table.put_item(Item={
            'userid': userid,
            'sentiment': sentiment,
            "timestamp": timestamp,
        })
    print("Calculated sentiment: ", sentiment)
    print("Put response: ", put_response)


def should_send_kitty(sentiment):
    return sentiment["Negative"] > 0.5

# load all the environmental variables
def load_vars():
    cat_token = os.environ['cat_token']
    bot_token = os.environ['bot_token']
    open_conversation_url = os.environ['open_conversation']
    get_cat_url = os.environ['get_cat']
    post_message_url = os.environ['post_message']
    return cat_token, bot_token, open_conversation_url, get_cat_url, post_message_url

# open direct conversation between kitty and user
def get_channel(user_id, bot_token, open_conversation_url):
    open_conversation_params = {
        'token': bot_token,
        'users': user_id
    }
    open_conversation_headers = {}
    response = requests.post(open_conversation_url, params=open_conversation_params, headers=open_conversation_headers).json()
    return response['channel']['id']


def send_random_cat(channel_id, cat_token, bot_token, get_cat_url, post_message_url):
    # get a cat
    cat_params = {'mime_types': 'gif'}
    cat_headers = {'x-api-key': cat_token}

    a_random_cat = requests.get(get_cat_url, params=cat_params, headers=cat_headers).json()[0]['url']

    post_msg_headers = {'token': bot_token}
    post_msg_params = {
        'token': bot_token,
        'channel': channel_id,
        'text': a_random_cat
    }
    response = requests.post(post_message_url, headers=post_msg_headers, params=post_msg_params)
    return {
        'statusCode': 200,
        'body': json.dumps(response.json())
    }
