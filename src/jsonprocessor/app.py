import boto3
import json
import re
from datetime import datetime


TIMESTAMP_REGEX = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z')


def flatten_json(input: dict) -> dict:
    """
    Method to flatten json structure recursively.

    Parameters:
        input (dict) -> Input is a dictionary.

    Returns:
        output (dict) -> Output is a flattened structure of the input.
    """
    output = {}

    def flatten(block, name=''):
        if type(block) is dict:
            for key in block:
                flatten(block[key], name + key + '_')
        elif type(block) is list:
            i = 0
            for element in block:
                flatten(element, name + '_')
                i += 1
        else:
            out_str = str(name[:-1])
            out = filter_rules(camel_to_underscores(out_str))
            output[out] = transform_block(block)
            output.pop('phone_data_type', None)
    flatten(input)
    return output


def filter_rules(key: str) -> str:
    if key.startswith('android_payload'):
        key = key.replace('android_payload_', '')
        # key = key[16:]
    return key


def transform_block(block):
    """Function to transform block's value"""
    res = None
    if block is None:
        res = "null"
    elif type(block) is str and TIMESTAMP_REGEX.match(block):
        datetime_obj = datetime.strptime(block, '%Y-%m-%dT%H:%M:%S.%fZ')
        res = str(datetime_obj.strftime('%Y-%m-%d %H:%M:%S'))
    else:
        res = block
    return res


def camel_to_underscores(string: str) -> str:
    """
    Converts a camel case string to underscores.

    Parameters:
        string (str) -> CamelCase string to be converted.

    Returns:
        transformed_string (str) -> Transformed Underscore Case string returned.
    """
    start_idx = [idx for idx, char in enumerate(
        string) if char.isupper()] + [len(string)]
    start_idx = [0] + start_idx
    words = [string[start: end]
             for start, end in zip(start_idx, start_idx[1:]) if string[start: end] is not '']
    transformed_string = ''
    for token in words:
        transformed_string += token.lower() + '_'
    return transformed_string[: -1]


def send_message_to_sqs(message):
    """Send messages to SQS Queue"""
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.eu-west-1.amazonaws.com/282415712953/json-file-processor-OutputQueue-1TGMAG26LQOW4'
    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageBody=json.dumps(message)
    )
    print(response['MessageId'])


def process_s3_object(bucket: str, key: str) -> list:
    """
    Retrives S3 object from the bucket and processes the data.

    Parameters:
        bucket (str) -> Bucket name to fetch the object from.
        key (str) -> Bucket prefix and the object name.

    Returns:
        res (list) -> List of processed JSON elements from the S3 object.
    """
    res = []
    s3 = boto3.client('s3')
    response = s3.get_object(
        Bucket=bucket,
        Key=key
    )
    records_list = json.loads(response['Body'].read().decode('utf-8'))
    for record in records_list:
        res.append(flatten_json(record))
    return res


def handler(event, context):
    """
    AWS Lambda Function handler to process JSON data and send it to SQS Queue.
    """
    for event in event['Records']:
        # This loop will run for every event that triggered Lambda function.
        records = json.loads(event['Sns']['Message'])
        for s3_record in records['Records']:
            # This loop will run for every object uploaded to the s3 bucket.
            bucket = s3_record['s3']['bucket']['name']
            key = s3_record['s3']['object']['key']
            # Process the object.
            messages = process_s3_object(bucket, key)
            for message in messages:
                send_message_to_sqs(message)
    return {
        'statusCode': 200,
        'body': 'Json file processed and sent to SQS Queue.'
    }
