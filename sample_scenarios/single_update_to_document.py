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
