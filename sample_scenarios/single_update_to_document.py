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

from sample_scenarios.sample_data import SampleData
from sample_scenarios.helpers import create_qldb_session

logger = getLogger(__name__)
basicConfig(level=INFO)


def update_documents(transaction_executor):
    logger.info('Updating some documents in the VehicleRegistration table...')

    for license_number, pending_amount in SampleData.PENDING_AMOUNT_VALUES_SINGLE_UPDATE.items():
        statement = 'UPDATE VehicleRegistration SET PendingPenaltyTicketAmount ' \
                    '= {amount} WHERE LicensePlateNumber = \'{license_number}\'' \
            .format(license_number=license_number, amount=pending_amount)

        logger.info('Updating PendingPenaltyTicketAmount for License Number: {license_number}'
                    ' to {amount}'.format(license_number=license_number, amount=pending_amount))

        transaction_executor.execute_statement(statement)


if __name__ == '__main__':
    """
    Updating documents in VehicleRegistration table in QLDB ledger.
    """
    try:
        with create_qldb_session() as session:
            session.execute_lambda(lambda executor: update_documents(executor),
                                   lambda retry_attempt: logger.info('Retrying due to OCC conflict...'))
            logger.info('Documents updated successfully!')
    except Exception:
        logger.exception('Error updating documents.')
