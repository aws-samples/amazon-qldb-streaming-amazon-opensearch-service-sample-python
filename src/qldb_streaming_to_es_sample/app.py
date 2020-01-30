from aws_kinesis_agg.deaggregator import deaggregate_records
import boto3
import os
from requests_aws4auth import AWS4Auth
from .helpers.filtered_records_generator import filtered_records_generator
from .clients.elasticsearch import ElasticsearchClient
from .constants import Constants

service = 'es'
session = boto3.Session()
credentials = session.get_credentials()
region = session.region_name
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
host = os.environ['ES_HOST']

elasticsearch_client = ElasticsearchClient(host=host, awsauth=awsauth)

TABLE_TO_INDEX_MAP = {Constants.PERSON_TABLENAME : Constants.PERSON_INDEX,
                   Constants.VEHICLE_REGISTRATION_TABLENAME : Constants.VEHICLE_REGISTRATION_INDEX}

def lambda_handler(event, context):
    """
    Triggered for a batch of kinesis records.
    Parses QLDB Journal streams and indexes documents to Elasticsearch for
    Person and Vehicle Registration Events.
    """
    raw_kinesis_records = event['Records']

    # Deaggregate all records in one call
    records = deaggregate_records(raw_kinesis_records)

    # Iterate through deaggregated records of Person and VehicleRegistration Table
    for record in filtered_records_generator(records,
                                             table_names=[Constants.PERSON_TABLENAME,
                                                          Constants.VEHICLE_REGISTRATION_TABLENAME]):
        table_name = record["table_info"]["tableName"]
        revision_data = record["revision_data"]
        revision_metadata = record["revision_metadata"]
        version = revision_metadata["version"]
        document = None

        if revision_data:
            # if record is for Person table and is an insert event
            if (table_name == Constants.PERSON_TABLENAME) and (version == 0) and \
                    __fields_are_present(Constants.PERSON_TABLE_FIELDS, revision_data):

                document = __create_document(Constants.PERSON_TABLE_FIELDS, revision_data)
                elasticsearch_client.index(index=TABLE_TO_INDEX_MAP[table_name],
                                           id=revision_metadata["id"], body=document, version=version)

            # if record is for VehicleRegistration table and is an insert or update event
            elif table_name == Constants.VEHICLE_REGISTRATION_TABLENAME and \
                    __fields_are_present(Constants.VEHICLE_REGISTRATION_TABLE_FIELDS, revision_data):
                document = __create_document(Constants.VEHICLE_REGISTRATION_TABLE_FIELDS, revision_data)
                elasticsearch_client.index(index=TABLE_TO_INDEX_MAP[table_name],
                                           id=revision_metadata["id"], body=document, version=version)

        else:
            # delete record
            elasticsearch_client.delete(index=TABLE_TO_INDEX_MAP[table_name],
                                           id=revision_metadata["id"], version=version)


    return {
        'statusCode': 200
    }


def __create_document(fields, revision_data):
    document = {}

    for field in fields:
        document[field] = revision_data[field]

    return document


def __fields_are_present(fields_list, revision_data):
    for field in fields_list:
        if not field in revision_data:
            return False

    return True
