import json
import urllib
from decimal import Decimal

import boto3
from environments import EnvironmentIntruder, EnvironmentNormal, EnvironmentOff
from events import Events
from hue_wrapper_v1 import HueWrapperV1 as HueWrapper

rekognition = boto3.client('rekognition')


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

    # TODO load active environment
    active_env_name = 'off'  # TODO remove

    # call the transition function form the currently active environment
    active_env_name = environments[active_env_name].transitions[event.name]()

    # TODO save active environment
    print('active env is ', active_env_name)


def lambda_handler(event, context):
    '''Demonstrates S3 trigger that uses
    Rekognition APIs to detect faces, labels and index faces in S3 Object.
    '''
    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(
        event['Records'][0]['s3']['object']['key'].encode('utf8'))

    print('*****called lambda function')
    try:
        # test if we know the person
        is_known = is_face_known(bucket, key,   'user-faces')
        print('is face known? ', is_known)

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
            environment_handler(Events.good_guy_entering, environments)
        else:
            environment_handler(Events.bad_guy_entering, environments)

        print('**** ending function call')

    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e
