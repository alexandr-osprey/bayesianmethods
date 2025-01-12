import json
from typed_logging.Enums import LogEventEnum, Constants
import pandas as pd
import numpy as np
from pgmpy.factors.discrete import DiscreteFactor
from typed_logging import LogMessage
from datetime import datetime, timezone
from typed_logging.LogEntry import LogEntry
from models.Footprint import Footprint

class JSONDeserializer:    
    def parse_entry(self, entry_dict: dict, instance: bool = False):
        message = entry_dict[Constants.MESSAGE]
        if instance:
            message = self._get_log_message_instance(message[Constants.LOG_EVENT], self.parse_message(message))
        log_entry = LogEntry(
            timestamp=self.parse_datetime(entry_dict[Constants.TIMESTAMP]),
            level=entry_dict[Constants.LEVEL],
            message=message,
            scope=entry_dict[Constants.SCOPE],
            module=entry_dict[Constants.MODULE],
            line=entry_dict[Constants.LINE],
            message_hash=entry_dict[Constants.MESSAGE_HASH]
        )
        
        return log_entry
    
    
    def parse_message(self, message: dict):
        obj_type = None
        if isinstance(message, dict) and message.get(Constants.OBJ_TYPE, None) != None:
            obj_type = message[Constants.OBJ_TYPE]
        if obj_type == Constants.DATAFRAME_TYPE:
            values = [self.parse_message(v) for v in message[Constants.VALUES]]
            index = [self.parse_message(v) for v in message[Constants.INDEX]]
            columns = message[Constants.COLUMNS]
            return pd.DataFrame(data=values, index=index, columns=columns)

        if obj_type == Constants.FOOTPRINT_TYPE:
            nodes = self.parse_message(message[Constants.NODES])
            return Footprint(nodes=nodes)
        
        if obj_type == Constants.NUMPY_ARRAY:
            values = self.parse_message(message[Constants.VALUES])
            return np.array(values)
    
        if obj_type == Constants.DISCRETE_FACTOR_TYPE:
            return DiscreteFactor(
                variables=message[Constants.VARIABLES],
                cardinality=message[Constants.CARDINALITY],
                values=message[Constants.VALUES])
        
        if isinstance(message, list):
            return [self.parse_message(v) for v in message]
        
        if isinstance(message, dict):
            parsed = {}
            for k, v in message.items():
                if k == Constants.LOG_EVENT:
                    continue

                p = self.parse_message(v)
                parsed[k] = p
            return parsed
        
        return message
    
    def _get_log_message_instance(self, log_event: str, data: dict):
        match LogEventEnum[log_event]:
            case LogEventEnum.InitialPMF:
                return LogMessage.InitialPMFMessage(**data)
            case LogEventEnum.EMFUpdate:
                return LogMessage.EMFUpdateMessage(**data)
            case LogEventEnum.PMFNodeUpdated:
                return LogMessage.PMFNodeUpdatedMessage(**data)
            case LogEventEnum.UpdatedPMF:
                return LogMessage.EvidencePropagatedInPMFMessage(**data)
            case _:
                raise Exception("Unknown log message type " + log_event)
    
    def parse_datetime(self, datestr: str) -> datetime:
        parsed_dt = datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S.%fZ")
        # Attach UTC timezone
        parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
        return parsed_dt
