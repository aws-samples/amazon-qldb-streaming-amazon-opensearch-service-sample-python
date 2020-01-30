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
                     WHERE r.LicensePlateNumber = \'{license_number}\'' \
            .format(license_number=vehicle_registration["LicensePlateNumber"],
                    table_name=Constants.VEHICLE_REGISTRATION_TABLE_NAME)

        logger.info('Deleting record from VehicleRegistration with License Number: {license_number}'
                    .format(license_number=vehicle_registration["LicensePlateNumber"]))

        transaction_executor.execute_statement(statement)


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
