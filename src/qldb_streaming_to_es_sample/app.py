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

        # if record is for Person table and is an insert event
        if (table_name == Constants.PERSON_TABLENAME) and (version == 0):
            if fields_are_present(Constants.PERSON_TABLE_FIELDS, revision_data):
                document = create_person_document(revision_data)
                elasticsearch_client.index(index=Constants.PERSON_INDEX,
                                           id=revision_metadata["id"], body=document, version=version)

        # if record is for VehicleRegistration table and is an insert or update event
        elif table_name == Constants.VEHICLE_REGISTRATION_TABLENAME:
            if fields_are_present(Constants.VEHICLE_REGISTRATION_TABLE_FIELDS, revision_data):
                document = create_vehicle_registration_document(revision_data)
                elasticsearch_client.index(index=Constants.VEHICLE_REGISTRATION_INDEX,
                                           id=revision_metadata["id"], body=document, version=version)
    return {
        'statusCode': 200
    }


def create_person_document(revision_data):
    return {"FirstName": revision_data["FirstName"],
            "LastName": revision_data["LastName"],
            "GovId": revision_data["GovId"]}


def create_vehicle_registration_document(revision_data):
    return {"VIN": revision_data["VIN"],
            "LicensePlateNumber": revision_data["LicensePlateNumber"],
            "State": revision_data["State"],
            "PendingPenaltyTicketAmount": revision_data["PendingPenaltyTicketAmount"]}


def fields_are_present(fields_list, revision_data):
    for field in fields_list:
        if not field in revision_data:
            return False

    return True
