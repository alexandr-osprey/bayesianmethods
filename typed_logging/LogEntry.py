from pydantic import BaseModel
from datetime import datetime
from typing import Union
from typed_logging.LogMessage import LogMessage

class LogEntry(BaseModel):
    timestamp: Union[datetime, str]
    level: str
    message: Union[dict, LogMessage]
    scope: str
    module: str
    line: int
    message_hash: str

    @classmethod
    def get_elastic_index(cls):
        mappings = {
            "properties": {
                "timestamp": { "type": "date"},
                "level": { "type": "keyword" },
                "message": { "type": "object" },
                "scope": { "type": "keyword" },
                "module": { "type": "text" },
                "line": { "type": "integer" },
                "message_hash": { "type": "text" }
            }
        }

        return mappings
