# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
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

try:
    host = os.environ['ES_HOST']
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

    for index in INDEXES:
        try:
            es.indices.create(index=index, body={'settings': {'index': {'gc_deletes': '1d'}}})
        except RequestError as e:
            if e.error == "resource_already_exists_exception":
                es.indices.put_settings(index=index, body={'gc_deletes': '1d'})
            else:
                raise e


@helper.update
def update(event, context):
    # no op
    pass


@helper.delete
def delete(event, context):
    # no op
    pass


def lambda_handler(event, context):
    helper(event, context)
