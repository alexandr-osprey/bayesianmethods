from runs_analysis.LogAnalyzer import LogAnalyzer
from typed_logging.LogMessage import PMFNodeUpdatedMessage
from runs_analysis.JSONDeserializer import JSONDeserializer
from datetime import datetime
import pgmpy
import inject
from typed_logging.LoggerConfig import LoggerConfig, LoggerModeEnum

def config_dependencies(binder: inject.Binder):
    binder.bind(LoggerConfig, LoggerConfig(mode=LoggerModeEnum.Analysis))

inject.configure(config_dependencies)

pgmpy.config.set_backend('numpy')
analyzer = LogAnalyzer()
analyzer.analyze_last_entries(2)
print("done")