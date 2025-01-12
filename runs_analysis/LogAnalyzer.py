import glob
from runs_analysis.LogParser import LogParser
from pydantic import BaseModel
from typed_logging.LogEntry import LogEntry
from runs_analysis.LogMessageComparer import LogMessageComparer
from typed_logging.LoggerConfig import LoggerConfig
from typed_logging.Enums import LoggerModeEnum
from datetime import datetime
from typed_logging.Logger import Logger

class LogAnalyzer(BaseModel):
    log_parser: LogParser = None
    message_comparer: LogMessageComparer = None
    runs_logger_mode: LoggerConfig = LoggerConfig(mode=LoggerModeEnum.Run)
    logger: Logger = None

    class Config:
        arbitrary_types_allowed = True

    def model_post_init(self, __context):
        self.logger = Logger()
        self.log_parser = LogParser()
        self.message_comparer = LogMessageComparer()
        return super().model_post_init(__context)
    
    def analyze_last_entries(self, n: int):
        now = datetime.now()
        self.logger.start_scope(f"analysis{now.strftime("%Y%m%dT%H%M%S")}")
        runs = self._parse_last_entries(n)
        run1 = runs[0][1]
        run2 = runs[1][1]
        length = len(run1)
        for i in range(length):
            self.message_comparer.compare_two_entries(run1[i], run2[i])
        self.logger.end_scope()

    def _parse_last_entries(self, n: int) -> dict[str, list[LogEntry]]:
        all_files = glob.glob(f'{self.runs_logger_mode.location}/*.json')
        all_files.sort()
        last_n = all_files[-n:]
        runs = []
        for file in last_n:
            runs.append((file, self.log_parser.parse(file)))
        
        return runs
