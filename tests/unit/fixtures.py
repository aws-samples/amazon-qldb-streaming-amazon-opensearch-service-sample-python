import amazon.ion.simpleion as ion
import base64
import pytest

def person_revision_details_ion_record(revision_version):
    person_revision_details_ion = """{
      recordType: "REVISION_DETAILS",
      payload: {
        tableInfo: {
          tableName: "Person",
        },
        revision: {
          data: {
            FirstName: "Nova",
            LastName: "Lewis",
            DOB: 1963-08-19T,
            GovId: "LEWISR261LL",
            GovIdType: "Driver License"          
            },
          metadata: {
            version: """ + str(revision_version) + """,
            id: "a8698243bnnmjy"
          }
        }
      }
    }"""

    return person_revision_details_ion

def vehicle_registration_revision_details_ion_record(revision_version):
    vehicle_registration_revision_details_ion = """{
      recordType: "REVISION_DETAILS",
      payload: {
        tableInfo: {
          tableName: "VehicleRegistration",
        },
        revision: {
          data: {
            VIN: "L12345",
            LicensePlateNumber: "1234567",
            State: "WA",
            PendingPenaltyTicketAmount: 127.5,
          },
          metadata: {
            version: """ + str(revision_version) + """,
            id: "2136bjkdc8"
          }
        }
      }
    }"""

    return vehicle_registration_revision_details_ion

def person_block_summary_ion_record():
    PERSON_BLOCK_SUMMARY_ION = """{
      recordType: "BLOCK_SUMMARY",
      payload: {
        transactionId: "0007KbqoyqAIch6XRbQ4iA",
        blockTimestamp: 2019-12-11T07:20:51.261Z,
        blockHash: {{lu425dAWsmvzxuNHTbn4ID4mLo0bWKkjLP2Uel4wrPQ=}},
        entriesHash: {{RNGQGcOKCGLCo5S+hs1eboanNrocIzRiqzzq1s99G/Q=}},
        previousBlockHash: {{pV28aszpqJH9LOO9oMsACDmXfdzdEW7HYxzuQVIjSDU=}},
        entriesHashList: [
          {{LmcGQjLlfScQQxbzaoglEpXpeN9bp7I/QUk690ncEpk=}},
          {{vJFOcsNRM14gsIBSEnwPhMVgRAWf/4EUW5gPYbtmDv0=}},
          {{KXJrG8t/KePERHasyztlv4kZPol4Q2buhWmy7iJrsiY=}},
          {{Lz3XWBwtWyBA/Lhj+UoLhbajPQ8Mk9N4j0HJlrm2OTg=}}
        ],
        transactionInfo: {
          statements: [
            {
              statement: "INSERT INTO Person <<\\n{\\n    'FirstName' : 'Testing new 600',\\n    'LastName' : 'Lewis',\\n    'DOB' : `1963-08-19T`,\\n    'GovId' : 'LEWISR261LL',\\n    'GovIdType' : 'Driver License',\\n    'Address' : '1719 University Street, Seattle, WA, 98109'\\n}\\n>>",
              startTime: 2019-12-11T07:20:51.223Z,
              statementDigest: {{t5wbRW+wIi/X0n3iPhFJtbt2qpzzgWkOXIFC4xJHp4o=}}
            }
          ],
          documents: {
            D35qd3e2prnJYmtKW6kok1: {
              tableName: "Person",
              tableId: "1SUXCa3wwV0GD7kV78RbSg",
              statements: [
                0
              ]
            }
          }
        },
        revisionSummaries: [
          {
            hash: {{vJFOcsNRM14gsIBSEnwPhMVgRAWf/4EUW5gPYbtmDv0=}},
            documentId: "D35qd3e2prnJYmtKW6kok1"
          }
        ]
      }
    }"""

    return PERSON_BLOCK_SUMMARY_ION


@pytest.fixture
def deaggregated_stream_records():
    def deaggregated_records(revision_version=0):
        return [{
            'kinesis': {
                'kinesisSchemaVersion': '1.0',
                'aggregated': True,
                'data': base64.b64encode(ion.dumps(ion.loads(person_block_summary_ion_record()))).decode("utf-8")
            }
        }, {
            'kinesis': {
                'kinesisSchemaVersion': '1.0',
                'aggregated': True,
                'data': base64.b64encode(
                    ion.dumps(ion.loads(person_revision_details_ion_record(revision_version)))).decode("utf-8")
            }
        }, {
            'kinesis': {
                'kinesisSchemaVersion': '1.0',
                'aggregated': True,
                'data': base64.b64encode(
                    ion.dumps(ion.loads(vehicle_registration_revision_details_ion_record(revision_version)))).decode("utf-8")
            }
        }]

    return deaggregated_records


@pytest.fixture
def elasticsearch_error():
    def client_error_helper(error_class):
        client_error = error_class(400, "error", "info");

        return client_error

    return client_error_helper
