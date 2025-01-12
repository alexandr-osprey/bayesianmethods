import logging
import json
from datetime import datetime, timezone
from pgmpy.factors.discrete import DiscreteFactor
import pandas as pd
from typed_logging.Enums import Constants
from typed_logging.LogMessage import LogMessage
from typed_logging.LogEntry import LogEntry
from models.Footprint import Footprint
from enum import Enum
import numpy as np

class JSONSerializer(logging.Formatter):
    def format(self, record):
        message = record.msg
        if not isinstance(message, LogMessage):
            raise Exception(f"Only {LogMessage} instances are supported for logging")

        message = self._serialize(message)
        mh = str(abs(hash(repr(message))))
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        iso_format = dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        log_record = LogEntry(
            timestamp=iso_format,
            level=record.levelname,
            message=message,
            message_hash=mh,
            scope=getattr(record, Constants.SCOPE, "default"),
            module=record.module,
            line=record.lineno,
        )

        return json.dumps(log_record, default=self._default_serializer, sort_keys=True)

    def _serialize(self, obj):
        if isinstance(obj, list):
            return [self._serialize(v) for v in obj]
        elif isinstance(obj, LogMessage):
            parsed_dict = {}
            for k, v in obj.__dict__.items():
                parsed = self._serialize(v)
                parsed_dict[k] = parsed
            return parsed_dict
        elif isinstance(obj, float):
            return round(obj, 3)
        elif isinstance(obj, (dict, tuple, str, int, bool, type(None))):
            return obj  # Standard JSON types
        elif isinstance(obj, pd.DataFrame):
            repr = {}
            repr[Constants.OBJ_TYPE] = Constants.DATAFRAME_TYPE
            repr[Constants.VALUES] = self._serialize(obj.values.tolist())
            repr[Constants.COLUMNS] = obj.columns.array.tolist()
            repr[Constants.INDEX] = self._serialize(obj.index.array.tolist())
            return repr
        elif isinstance(obj, DiscreteFactor):
            repr = {}
            repr[Constants.OBJ_TYPE] = Constants.DISCRETE_FACTOR_TYPE
            repr[Constants.VARIABLES] = obj.variables
            repr[Constants.VALUES] =  self._serialize(obj.values.tolist())
            repr[Constants.CARDINALITY] = obj.cardinality.tolist()
            repr[Constants.REPR] = str(obj)
            return repr
        elif isinstance(obj, Footprint):
            repr = {}
            repr[Constants.OBJ_TYPE] = Constants.FOOTPRINT_TYPE
            repr[Constants.NODES] = self._serialize(list(obj.nodes))
            return repr
        elif isinstance(obj, np.ndarray):
            repr = {}
            repr[Constants.OBJ_TYPE] = Constants.NUMPY_ARRAY
            repr[Constants.VALUES] = self._serialize(obj.tolist())
            return repr
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Enum):
            return obj.name
        elif hasattr(obj, "__dict__"):
            return vars(obj)
        else:
            return str(obj)
        
    def _default_serializer(self, obj):
        """Fallback serializer for the `json.dumps` call."""
        return self._serialize(obj)