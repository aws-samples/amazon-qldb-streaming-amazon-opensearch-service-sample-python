from __future__ import print_function
from crhelper import CfnResource
import logging
import boto3
import os
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection, RequestError

logger = logging.getLogger(__name__)
# Initialise the helper, all inputs are optional, this example shows the defaults
helper = CfnResource(json_logging=False, log_level='DEBUG', boto_level='CRITICAL')

service = 'es'
INDEXES = ["person_index", "vehicle_registration_index"]
es = None
es_boto = None

try:
    host = os.environ['ES_HOST']
    user_pool_id = os.environ['USER_POOL_ID']
    identity_pool_id = os.environ['IDENTITY_POOL_ID']
    es_domain_name = os.environ['ES_DOMAIN_NAME']
    role_arn = os.environ['ROLE']

    es_boto = boto3.client('es')
    session = boto3.Session()
    credentials = session.get_credentials()
    region = session.region_name
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        retry_on_timeout=True,
        max_retries=3
    )

except Exception as e:
    helper.init_failure(e)


@helper.create
def create(event, context):
    logger.info("Initiating index creation")
    helper.Data.update({"Status": "Initiated"})

    es_boto.update_elasticsearch_domain_config(DomainName=es_domain_name, CognitoOptions={'Enabled': True,
                                                                                          'UserPoolId': user_pool_id,
                                                                                          'IdentityPoolId': identity_pool_id,
                                                                                          'RoleArn': role_arn})

    for index in INDEXES:
        try:
            es.indices.create(index=index, body={'settings': {'index': {'gc_deletes': '1d'}}})
        except RequestError as e:
            if e.error == "resource_already_exists_exception":
                es.indices.put_settings(index=index, body={'gc_deletes': '1d'})
            else:
                raise e


def lambda_handler(event, context):
    helper(event, context)
