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