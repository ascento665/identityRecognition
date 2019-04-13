import json
import urllib
from decimal import Decimal

import boto3
from environments import EnvironmentIntruder, EnvironmentNormal, EnvironmentOff
from events import Events
from hue_wrapper_v1 import HueWrapperV1 as HueWrapper

rekognition = boto3.client('rekognition')
s3 = boto3.resource('s3')


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


def environment_handler(event, environments):
    """
    main event handling function of state machine

    Arguments
    ---------
    event (enum class Events): the event which occured

    Returns
    -------
    void
    """

    # load the currently active environment from a json in s3
    state_object = s3.Object('asc-user-db', 'state-info/state.json')
    file_content = state_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    # returns a string containing the name
    old_active_env_name = json_content['active_env']

    # call the transition function form the currently active environment
    new_active_env_name = environments[old_active_env_name].transitions[event.name](
    )

    # update the active state and save to json in s3
    json_content['active_env'] = new_active_env_name
    state_object.put(Body=bytes(json.dumps(
        json_content, indent=2).encode('utf-8')))

    # logging
    print('[environment_handler] changed env from {} to {}'.format(
        old_active_env_name, new_active_env_name))

    return


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

        # prepare environment handler
        # SETUP add more environments here
        light = HueWrapper()
        environments = {
            'off': EnvironmentOff(light),
            'normal': EnvironmentNormal(light),
            'intruder': EnvironmentIntruder(light),
        }

        # call appropiate event on environment handler
        if is_known:
            # logging
            print('[lambda_handler] received face which is known')
            environment_handler(Events.good_guy_entering, environments)

        else:
            # logging
            print('[lambda_handler] received face which is not known')
            environment_handler(Events.bad_guy_entering, environments)

    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e
