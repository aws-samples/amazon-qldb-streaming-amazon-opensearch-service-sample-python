import sys, os

sys.path.append(os.path.abspath('../../'))
import aws_kinesis_agg
from aws_kinesis_agg.deaggregator import deaggregate_records
from .fixtures import deaggregated_stream_records
from .fixtures import elasticsearch_error
from src.qldb_streaming_to_es_sample.constants import Constants
from unittest.mock import call
from .test_constants import TestConstants
import unittest

sys.path.append(os.path.abspath('../../'))
os.environ["ES_HOST"] = "htttp://es"

from src.qldb_streaming_to_es_sample import app

PERSON_INSERT_CALL = call(body=TestConstants.PERSON_DATA,
                          id=TestConstants.PERSON_METADATA_ID,
                          index=Constants.PERSON_INDEX,
                          version=0)

VEHICLE_REGISTRATION_INSERT_CALL = call(body=TestConstants.VEHICLE_REGISTRATION_DATA,
                                        id=TestConstants.VEHICLE_REGISTRATION_METADATA_ID,
                                        index=Constants.VEHICLE_REGISTRATION_INDEX,
                                        version=0)

test_case_instance = unittest.TestCase('__init__')

def test_indexing_records_for_inserts(mocker, deaggregated_stream_records):
    deaggregated_records = deaggregated_stream_records(revision_version=0)

    # Mock
    mocker.patch('src.qldb_streaming_to_es_sample.app.deaggregate_records', return_value=deaggregated_records)
    mocker.patch('src.qldb_streaming_to_es_sample.app.elasticsearch_client.index', return_value={"status": "success"})

    # Trigger
    response = app.lambda_handler({"Records": ["a dummy record"]}, "")

    # Verify
    calls = [PERSON_INSERT_CALL, VEHICLE_REGISTRATION_INSERT_CALL]

    app.elasticsearch_client.index.assert_has_calls(calls)
    assert response["statusCode"] == 200


def test_no_indexing_person_record_for_updates(mocker, deaggregated_stream_records):
    deaggregated_records = deaggregated_stream_records(revision_version=1)

    # Mock
    mocker.patch('src.qldb_streaming_to_es_sample.app.deaggregate_records', return_value=deaggregated_records)
    mocker.patch('src.qldb_streaming_to_es_sample.app.elasticsearch_client.index', return_value={"status": "success"})

    # Trigger
    reponse = app.lambda_handler({"Records": ["a dummy record"]}, "")

    # Verify
    app.elasticsearch_client.index.assert_called_once_with(body=TestConstants.VEHICLE_REGISTRATION_DATA,
                                                           id=TestConstants.VEHICLE_REGISTRATION_METADATA_ID,
                                                           index=Constants.VEHICLE_REGISTRATION_INDEX,
                                                           version=1)

    assert reponse["statusCode"] == 200


def test_config_exceptions_are_bubbled(mocker, deaggregated_stream_records, elasticsearch_error):
    deaggregated_records = deaggregated_stream_records(revision_version=1)

    # Mock
    mocker.patch('src.qldb_streaming_to_es_sample.app.deaggregate_records', return_value=deaggregated_records)


    for error_class in TestConstants.EXCEPTIONS_THAT_SHOULD_BE_BUBBLED:
        error = elasticsearch_error(error_class)
        mocker.patch('src.qldb_streaming_to_es_sample.app.elasticsearch_client.index', side_effect=[error, None])

        # Verify
        test_case_instance.assertRaises(error_class, app.lambda_handler,{"Records": ["a dummy record"]}, "")



