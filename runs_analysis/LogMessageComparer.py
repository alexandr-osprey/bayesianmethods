from pydantic import BaseModel
from runs_analysis.LogDiffers import LogDiffers
from pgmpy.factors.discrete import DiscreteFactor
import numpy as np
from typed_logging.Enums import Constants, LogEventEnum
from typed_logging.Logger import Logger
from typed_logging.LogEntry import LogEntry
from runs_analysis.JSONDeserializer import JSONDeserializer
import torch

class LogMessageComparer(BaseModel):
    logger: Logger = None
    deserializer: JSONDeserializer = JSONDeserializer()

    class Config:
        arbitrary_types_allowed = True 

    def model_post_init(self, __context):
        self.logger = Logger()
        return super().model_post_init(__context)
    
    def compare_two_entries(self, e1: LogEntry, e2: LogEntry):
        m1 = e1.message
        m2 = e2.message
        if type(m1) != type(m2):
            raise Exception("Messages have different types")

        if len(m1) != len(m2):
            raise Exception("Messages have different lengths")

        for k in m1.keys():
            v1 = m1[k]
            v2 = m2[k]

            if type(v1) != type(v2):
                raise Exception(f"types of {k}: {v1}, {v2} are different")
            
            differ = False
            le = LogEventEnum[m1[Constants.LOG_EVENT]]

            parsed1 = self.deserializer.parse_message(v1)
            parsed2 = self.deserializer.parse_message(v2)

            delta = None
            if isinstance(parsed1, (DiscreteFactor)):
                delta = parsed1 + (parsed2 * -1)
            
            if isinstance(parsed1, (np.ndarray)):
                delta = np.array(parsed1) + (np.array(parsed2) * -1)

            if delta is not None:
                self.logger.start_scope(e1.scope)
                self.logger.info(LogDiffers(log_event=le, field=k, v1=v1, v2=v2, mh1=e1.message_hash, mh2=e2.message_hash, delta=delta))
                self.logger.end_scope()
        return differ
