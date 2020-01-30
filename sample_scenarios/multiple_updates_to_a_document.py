from logging import basicConfig, getLogger, INFO

from sample_scenarios.sample_data import convert_object_to_ion, SampleData, get_document_ids_from_dml_results
from sample_scenarios.helpers import create_qldb_session
from decimal import Decimal
from sample_scenarios.constants import Constants

logger = getLogger(__name__)
basicConfig(level=INFO)


def update_documents(transaction_executor):
    logger.info('Updating some documents multiple times in the {} table...'). \
        format(Constants.VEHICLE_REGISTRATION_TABLE_NAME)

    for license_number, pending_amounts in SampleData.PENDING_AMOUNT_VALUES_FOR_MULTIPLE_UPDATES.items():

        for pending_amount in pending_amounts:
            statement = 'UPDATE {table_name} SET PendingPenaltyTicketAmount ' \
                        '= {amount} WHERE LicensePlateNumber = \'{license_number}\'' \
                .format(license_number=license_number, amount=pending_amount,
                        table_name=Constants.VEHICLE_REGISTRATION_TABLE_NAME)

            logger.info('Updating PendingPenaltyTicketAmount for License Number: {license_number}'
                        ' to {amount}'.format(license_number=license_number, amount=pending_amount))

            transaction_executor.execute_statement(statement)


if __name__ == '__main__':
    """
    Updating documents multiple times in VehicleRegistration table.
    """
    try:
        with create_qldb_session() as session:
            session.execute_lambda(lambda executor: update_documents(executor),
                                   lambda retry_attempt: logger.info('Retrying due to OCC conflict...'))
            logger.info('Documents updated successfully!')
    except Exception:
        logger.exception('Error updating documents.')