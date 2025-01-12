from pydantic import BaseModel, Field
from typed_logging.Enums import LoggerModeEnum
import logging

class LoggerConfig(BaseModel):
    mode: LoggerModeEnum = Field(default_factory=lambda: LoggerModeEnum.Run)
    location: str = None
    log_level: int = Field(default_factory=lambda: logging.INFO)

    def model_post_init(self, __context):
        if self.location is not None:
            return
        
        runs_location = 'logs/runs'
        analysis_location = 'logs/analysis'

        if self.mode == LoggerModeEnum.Run:
            self.location = runs_location
        elif self.mode == LoggerModeEnum.Analysis:
            self.location = analysis_location
        else:
            raise Exception("Unknown log mode")
