import amazon.ion.simpleion as ion
import base64

REVISION_DETAILS_RECORD_TYPE = "REVISION_DETAILS"


def filtered_records_generator(kinesis_deaggregate_records, table_names=None):
    for record in kinesis_deaggregate_records:
        # Kinesis data in Python Lambdas is base64 encoded
        payload = base64.b64decode(record['kinesis']['data'])
        # payload is the actual ion binary record published by QLDB to the stream
        ion_record = ion.loads(payload)
        print("Ion record: ", (ion.dumps(ion_record, binary=False)))

        if ("recordType" in ion_record) and (ion_record["recordType"] == REVISION_DETAILS_RECORD_TYPE):
            table_info = get_table_info_from_revision_record(ion_record)

            if not table_names or (table_info and (table_info["tableName"] in table_names)):
                revision_data, revision_metadata = get_data_metdata_from_revision_record(ion_record)

                yield {"table_info": table_info,
                       "revision_data": revision_data,
                       "revision_metadata": revision_metadata}


def get_data_metdata_from_revision_record(revision_record):
    """
    Retrieves the data block from revision Revision Record

    Parameters:
       revision_record (string): The ion representation of Revision record from QLDB Streams
    """

    revision_data = None
    revision_metadata = None

    if ("payload" in revision_record) and ("revision" in revision_record["payload"]):
        if "data" in revision_record["payload"]["revision"]:
            revision_data = revision_record["payload"]["revision"]["data"]
        if "metadata" in revision_record["payload"]["revision"]:
            revision_metadata = revision_record["payload"]["revision"]["metadata"]

    return [revision_data, revision_metadata]


def get_table_info_from_revision_record(revision_record):
    """
    Retrieves the table information block from revision Revision Record
    Table information contains the table name and table id

    Parameters:
       revision_record (string): The ion representation of Revision record from QLDB Streams
    """

    if ("payload" in revision_record) and "tableInfo" in revision_record["payload"]:
        return revision_record["payload"]["tableInfo"]
