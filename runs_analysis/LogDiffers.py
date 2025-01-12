from typed_logging.LogMessage import LogMessage
from typed_logging.Enums import LogEventEnum
from typing import Union
from pgmpy.factors.discrete import DiscreteFactor
from pydantic import Field
import typing

class LogDiffers(LogMessage):
    log_event: LogEventEnum
    field: str
    v1: Union[list, dict]
    v2: Union[list, dict]
    mh1: str
    mh2: str
    delta: typing.Any
