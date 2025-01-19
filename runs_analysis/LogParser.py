import json
from runs_analysis.JSONDeserializer import JSONDeserializer
from typed_logging.LogEntry import LogEntry

class LogParser:
    def __init__(self):
        self.parser = JSONDeserializer()

    def parse(self, path: str, parse_message = False) -> list[LogEntry]:
        parsed_entries = []
        with open(path, 'r') as f:
            while entry_str := f.readline():
                entry_json = json.loads(entry_str)
                parsed = self.parser.parse_entry(entry_json, parse_message=parse_message)
                parsed_entries.append(parsed)
        
        return parsed_entries
    