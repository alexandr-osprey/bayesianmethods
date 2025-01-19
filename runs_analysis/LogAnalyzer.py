import glob
from runs_analysis.LogParser import LogParser
from pydantic import BaseModel
from typed_logging.LogEntry import LogEntry
from runs_analysis.LogMessageComparer import LogMessageComparer
from typed_logging.LoggerConfig import LoggerConfig
from typed_logging.Enums import LoggerModeEnum
from datetime import datetime
from typed_logging.Logger import Logger
import pandas as pd
from typed_logging.Enums import LogEventEnum
from typed_logging.LogMessage import EvidencePropagatedInPMFMessage
from pgmpy.factors.discrete import DiscreteFactor
import numpy as np

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

    def _parse_last_entries(self, n: int, parse_message = False) -> list[tuple[str, list[LogEntry]]]:
        all_files = glob.glob(f'{self.runs_logger_mode.location}/*.json')
        all_files.sort()
        last_n = all_files[-n:]
        runs = []
        for file in last_n:
            runs.append((file, self.log_parser.parse(file, parse_message=parse_message)))
        
        return runs
    
    def parse_last_entry(self) -> list[LogEntry]:
        return self._parse_last_entries(1, parse_message=True)[0][1]
    
    def get_pmf_dynamics(self) -> pd.DataFrame:
        all_log_entries = self.parse_last_entry()
        messages = self._get_evidence_propaged_messages(all_log_entries)
        initial = messages[0][1].initial
        skills = [d.variables[0] for d in initial]
        skills.sort()

        state_names = []
        for d in initial:
            for name in d.state_names.values():
                state_names.extend(name)
        state_names = sorted(set(state_names))
        columns = [ 'skill', 'evidence' ] + state_names
        values = []
        values.extend(self._factors_to_list(state_names, initial, 'initial'))
        for i in range(len(messages)):
            m = messages[i]
            evidence = m[0].split('__')[1]
            updated = m[1].updated
            values.extend(self._factors_to_list(state_names, updated, evidence))
        
        df = pd.DataFrame(data=values, columns=columns)
        return df
    
    def _factors_to_list(self, state_names: list[str], factors: list[DiscreteFactor], evidence: str) -> list:
        result = []
        for f in factors:
            v = []
            skill = f.variables[0]
            v.append(skill)
            v.append(evidence)
            for sn in state_names:
                if sn not in f.state_names[skill]:
                    v.append(0)
                    continue
                
                index = f.state_names[skill].index(sn)
                v.append(f.values[index])
            result.append(v)
        
        return result
    
    def _get_evidence_propaged_messages(self, entries: list[LogEntry]) -> list[tuple[str, EvidencePropagatedInPMFMessage]]:
        return [(e.scope, e.message) for e in entries if e.message.log_event == LogEventEnum.UpdatedPMF]
