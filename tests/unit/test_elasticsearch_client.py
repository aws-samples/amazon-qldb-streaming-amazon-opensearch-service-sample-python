from src.qldb_streaming_to_es_sample.clients.elasticsearch import ElasticsearchClient
from requests_aws4auth import AWS4Auth
from .test_constants import TestConstants
from src.qldb_streaming_to_es_sample.constants import Constants
from unittest.mock import MagicMock
from .fixtures import elasticsearch_error
import unittest

region = 'us-east-1'
service = 'es'
awsauth = AWS4Auth("access_key", "secret_key", region, service, "session_token")
host = "elasticsearch_host"

elasticsearch_client = ElasticsearchClient(host=host, awsauth=awsauth)

def test_indexing():

    # Mock
    elasticsearch_client.es_client.index = MagicMock(return_value={"status":"success"})

    # Trigger
    response= elasticsearch_client.index(body = TestConstants.PERSON_DATA, version=1,
                                         index = Constants.PERSON_INDEX, id = TestConstants.PERSON_DATA["GovId"])

    # Verify
    elasticsearch_client.es_client.index.assert_called_once_with(body=TestConstants.PERSON_DATA,
                          id=TestConstants.PERSON_DATA["GovId"],
                          index=Constants.PERSON_INDEX,
                          version=1,version_type='external')


def test_bad_input_exceptions_are_handled_for_indexing(elasticsearch_error):

    for error_class in TestConstants.EXCEPTIONS_THAT_SHOULD_BE_HANDLED:
        error = elasticsearch_error(error_class)

        # Mock
        elasticsearch_client.es_client.index = MagicMock(side_effect=[error, None])

        # Trigger
        response = elasticsearch_client.index(body=TestConstants.PERSON_DATA, version=1,
                                              index=Constants.PERSON_INDEX, id=TestConstants.PERSON_DATA["GovId"])


        # Verify
        assert response == None


def test_deletion():

    # Mock
    elasticsearch_client.es_client.delete = MagicMock(return_value={"status":"success"})

    # Trigger
    response= elasticsearch_client.delete(version=1,
                                         index = Constants.PERSON_INDEX, id = TestConstants.PERSON_DATA["GovId"])

    # Verify
    elasticsearch_client.es_client.delete.assert_called_once_with(id=TestConstants.PERSON_DATA["GovId"],
                          index=Constants.PERSON_INDEX,
                          version=1,version_type='external')


def test_bad_input_exceptions_are_handled_for_deletion(elasticsearch_error):

    for error_class in TestConstants.EXCEPTIONS_THAT_SHOULD_BE_HANDLED:
        error = elasticsearch_error(error_class)

        # Mock
        elasticsearch_client.es_client.delete = MagicMock(side_effect=[error, None])

        # Trigger
        response = elasticsearch_client.delete(version=1, index=Constants.PERSON_INDEX,
                                               id=TestConstants.PERSON_DATA["GovId"])


        # Verify
        assert response == None