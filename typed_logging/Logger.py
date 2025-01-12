import logging
from datetime import datetime
import os
from typed_logging.JSONSerializer import JSONSerializer
from typed_logging.LogMessage import LogMessage
from typed_logging.LoggerConfig import LoggerConfig
from typed_logging.elastic.ElasticsearchHandler import ElasticsearchHandler, ElasticConfig
import inject

class Logger:
    _instance = None
    _scope = None

    def __new__(cls):
        if cls._instance is None:
            logger_config = inject.instance(LoggerConfig)
            if logger_config is None:
                raise Exception("Logger config not provided")
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._logger = logging.getLogger("json_logger")
            logger = cls._instance._logger
            cls._instance._adapter = logging.LoggerAdapter(cls._instance._logger, merge_extra=True)
            logger.setLevel(logger_config.log_level)

            directory = logger_config.location
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            log_file = f"{directory}/log_{timestamp}.json"
            if not os.path.exists(directory):
                os.makedirs(directory)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logger_config.log_level)

            formatter = JSONSerializer()
            file_handler.setFormatter(formatter)

            logger.addHandler(file_handler)

            # Elasticsearch host
            elastic_config = ElasticConfig(host="https://localhost:9200")
            es_handler = ElasticsearchHandler(elastic_config)
            es_handler.setFormatter(formatter)
            logger.addHandler(es_handler)
        return cls._instance
    
    def info(self, msg: LogMessage, *args, **kwargs):
        if not isinstance(msg, LogMessage):
            raise Exception(f"Only {LogMessage} instances are supported for logging")

        self._instance._adapter.info(msg, *args, stacklevel=2)

    def start_scope(self, scope):
        if self._scope is None:
            self._scope = ScopeFilter()
            self._instance._logger.addFilter(self._scope)
        if isinstance(scope, tuple):
            scope = '_'.join([str(t) for t in scope])
        self._scope.add(scope)
    
    def end_scope(self):
        self._scope.remove()
        #self._instance._logger.removeFilter(self._scope)

class ScopeFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.values = []
        self.scope = ''

    def filter(self, record):
        record.scope = self.scope
        return True
    
    def add(self, value):
        self.values.append(value)
        self.scope = '__'.join(self.values)
    
    def remove(self):
        self.values = self.values[:-1]
        self.scope = '__'.join(self.values)
