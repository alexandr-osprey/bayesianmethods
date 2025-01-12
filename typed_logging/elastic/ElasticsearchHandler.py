import logging
from elasticsearch import Elasticsearch
from pydantic import BaseModel
from typed_logging.LogEntry import LogEntry
import ssl



class ElasticConfig(BaseModel):
    host: str

class ElasticsearchHandler(logging.Handler):
    def __init__(self, config: ElasticConfig):
        super().__init__()
        ctx = ssl.create_default_context()
        ctx.load_verify_locations("typed_logging/elastic/elastic.crt")
        ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
        self.client = Elasticsearch(hosts=config.host, ssl_context=ctx, basic_auth=('elastic', 'pass4321'))
        print(self.client.info().body)
        self._ensure_index()

    def emit(self, record):
        log_entry = self.format(record)
        self.client.index(
            index="main",
            document=log_entry)
        
    def _ensure_index(self):
        if not self.client.indices.exists(index="main"):
            mappings = LogEntry.get_elastic_index()
            self.client.indices.create(index="main", mappings=mappings)
