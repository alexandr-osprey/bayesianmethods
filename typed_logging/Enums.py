from enum import Enum
from dataclasses import dataclass

class LogEventEnum(Enum):
    EMFUpdate = 20,
    PMFNodeUpdated = 30,
    UpdatedPMF = 160,
    LogDiffers = 200,
    EvidenceCalculated = 250

class LoggerModeEnum(Enum):
    Run = 10,
    Analysis = 20

@dataclass(frozen=True)
class Constants:
    OBJ_TYPE='_obj_type'
    DATAFRAME_TYPE='DataFrame'
    DISCRETE_FACTOR_TYPE='DiscreteFactor'
    FOOTPRINT_TYPE='Footprint'
    NUMPY_ARRAY='NumpyArray'
    VARIABLES='variables'
    CARDINALITY='cardinality'
    INDEX='index'
    COLUMNS='columns'
    VALUES='values'
    REPR='repr'
    NODES='nodes'
    LOG_EVENT='log_event'
    MESSAGE='message'
    SCOPE='scope'
    TIMESTAMP='timestamp'
    MODULE='module'
    LINE='line'
    LEVEL='level'
    TIMESTAMP_FORMAT='%Y-%m-%d %H:%M:%S'
    MESSAGE_HASH='message_hash'
    STATE_NAMES='state_names'
