import json
from runs_analysis.JSONDeserializer import JSONDeserializer

class LogParser:
    def __init__(self):
        self.parser = JSONDeserializer()

    def parse(self, path):
        parsed_entries = []
        with open(path, 'r') as f:
            while entry_str := f.readline():
                entry_json = json.loads(entry_str)
                parsed = self.parser.parse_entry(entry_json)
                parsed_entries.append(parsed)
        
        return parsed_entries
    