import json
import urllib
from decimal import Decimal

import boto3

rekognition = boto3.client('rekognition')
lambda_client = boto3.client('lambda')


# ------------ Helper Functions ---------------

def is_face_known(bucket, key, collection_id):
    """
    Parameters
    ----------
    bucket: the bucket from s3
    key: the key from s3
    collection_id (string): name of the collection

    Returns
    ------
    bool: if found or not
    """
    response = rekognition.search_faces_by_image(
        CollectionId=collection_id,
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': key,
            }
        },
        MaxFaces=10,
    )

    return response['FaceMatches'] != []


def lambda_handler(event, context):
    '''Demonstrates S3 trigger that uses
    Rekognition APIs to detect faces, labels and index faces in S3 Object.
    '''
    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(
        event['Records'][0]['s3']['object']['key'].encode('utf8'))

    try:
        # test if we know the person
        is_known = is_face_known(bucket, key,   'user-faces')

        # call appropiate event on environment handler
        if is_known:
            # logging
            print('[lambda_handler] received face which is known')
            payload_dict = {'event': 'good_guy_entering'}

        else:
            # logging
            print('[lambda_handler] received face which is not known')
            payload_dict = {'event': 'bad_guy_entering'}

        # save dict to json locally
        response = lambda_client.invoke(
            FunctionName='environmentHandler',
            InvocationType='Event',
            LogType='None',
            Payload=bytes(json.dumps(
                payload_dict, indent=2).encode('utf-8')),
        )

    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e
