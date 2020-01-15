from decimal import Decimal
from elasticsearch import ConnectionError,ImproperlyConfigured,SSLError
from elasticsearch import SerializationError, ConflictError, RequestError

class TestConstants:
    PERSON_DATA = {'FirstName': 'Nova', 'GovId': 'LEWISR261LL', 'LastName': 'Lewis'}
    VEHICLE_REGISTRATION_DATA = {'VIN': 'L12345', 'LicensePlateNumber': '1234567',
                                  'State': 'WA', 'PendingPenaltyTicketAmount': Decimal('127.5')}
    PERSON_METADATA_ID = "a8698243bnnmjy"
    VEHICLE_REGISTRATION_METADATA_ID = "2136bjkdc8"

    EXCEPTIONS_THAT_SHOULD_BE_BUBBLED = [ConnectionError, ImproperlyConfigured, SSLError]
    EXCEPTIONS_THAT_SHOULD_BE_HANDLED = [SerializationError, ConflictError, RequestError]