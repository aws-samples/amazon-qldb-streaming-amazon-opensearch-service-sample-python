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
from logging import basicConfig, getLogger, INFO

from sample_scenarios.constants import Constants
from sample_scenarios.sample_data import convert_object_to_ion, SampleData, get_document_ids_from_dml_results
from sample_scenarios.helpers import create_qldb_session
from decimal import Decimal

logger = getLogger(__name__)
basicConfig(level=INFO)


def delete_documents(transaction_executor):

    logger.info('Updating some documents in the {} table...'.format(Constants.VEHICLE_REGISTRATION_TABLE_NAME))

    for vehicle_registration in SampleData.VEHICLE_REGISTRATION:
        statement = 'DELETE FROM {table_name} AS r \
                     WHERE r.LicensePlateNumber = ?' \
            .format(table_name=Constants.VEHICLE_REGISTRATION_TABLE_NAME)

        logger.info('Deleting record from VehicleRegistration with License Number: {license_number}'
                    .format(license_number=vehicle_registration["LicensePlateNumber"]))

        transaction_executor.execute_statement(statement, vehicle_registration["LicensePlateNumber"])


if __name__ == '__main__':
    """
    Delete documents inserted by 'insert_documents.py'.
    """
    try:
        with create_qldb_session() as session:
            session.execute_lambda(lambda executor: delete_documents(executor),
                                   lambda retry_attempt: logger.info('Retrying due to OCC conflict...'))
            logger.info('Documents deleted successfully!')
    except Exception:
        logger.exception('Error deleted documents.')
