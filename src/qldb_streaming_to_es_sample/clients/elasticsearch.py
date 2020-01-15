from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch import SerializationError, ConflictError, RequestError


class ElasticsearchClient:
    """
    Elasticsearch wrapper
    """
    es_client = None

    def __init__(self, host, awsauth):
        self.es_client = Elasticsearch(
            hosts=[{'host': host, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            retry_on_timeout=True,
            max_retries=0
        )

    def index(self, index, id, body, version):
        """
        Indexes documents to elasticsearch.
        Uses external version support to handle duplicates.
        https://www.elastic.co/blog/elasticsearch-versioning-support
        https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-index_.html#index-version-types
        """
        try:
            response = self.es_client.index(index=index, id=id,
                                            body=body, version=version, version_type="external")

            print("Indexed document with id: {id}, body: {body}"
                  " and version: {version}".format(id=id, body=body,
                                                   version=version))

            return response

        except (SerializationError, ConflictError,
                RequestError) as e:  # https://elasticsearch-py.readthedocs.io/en/master/exceptions.html#elasticsearch.ElasticsearchException
            print("Elasticsearch Exception occured while indexing id={id}, body={body} and"
                  "version={version}. Error: {error}".format(id=id, body=body, version=version,
                                                             error=str(e)))
            return None
