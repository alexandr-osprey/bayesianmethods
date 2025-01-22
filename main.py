# %%
from pgmpy.factors.discrete import TabularCPD, DiscreteFactor
from pgmpy.inference import BeliefPropagationWithMessagePassing as BPM
import matplotlib.pyplot as plt
import networkx as nx
from data.FullDataBuilder import FullDataBuilder
from propagation.BeliefUpdater import BeliefUpdater
from models.EMFCollection import EMFCollection
from models.PMFBuilder import PMFBuilder
from typed_logging.Logger import Logger
from typed_logging.LoggerConfig import LoggerConfig, LoggerModeEnum
from datetime import datetime
import pgmpy
import inject
from visualization.PMFVisualization import PMFVisualization
from runs_analysis.LogAnalyzer import LogAnalyzer

def print_cpd(cpd):
    backup = TabularCPD._truncate_strtable
    TabularCPD._truncate_strtable = lambda self, x: x
    print(cpd)
    TabularCPD._truncate_strtable = backup

def get_pmf_emfs():
    db = FullDataBuilder()
    initial_pmf = db.create_initial_pmf()
    all_skills = [str(n) for n in initial_pmf.nodes]
    full_model = db.create_full_model(initial_pmf)
    q_matrix = db.create_q_matrix(all_skills, full_model)
    emfs = db.create_emfs(full_model, q_matrix, skills=all_skills)
    emf_collection = EMFCollection(emfs=emfs)
    pmf_builder = PMFBuilder(full_model=full_model, emf_footprints=emf_collection.get_footprints(), skills=all_skills)
    pmf = pmf_builder.build()
    return (pmf, emf_collection)

def config_run_dependencies(binder: inject.Binder):
    binder.bind(LoggerConfig, LoggerConfig(mode=LoggerModeEnum.Run))

try:
    inject.configure(config_run_dependencies)
except:
    pass

pgmpy.config.set_backend('numpy')
pmf, emf_collection = get_pmf_emfs()

visualization = PMFVisualization(pmf=pmf)

logger = Logger()
now = datetime.now()
scope = f"run{now.strftime("%Y%m%dT%H%M%S")}"
logger.start_scope(scope)
belief_updater = BeliefUpdater(pmf=pmf, emfs=emf_collection)
visualization.pmf_map()
#visualization.pmf_dist("before")
skill_1_true = DiscreteFactor(["s1"], cardinality=[2], values=[0, 1])
#belief_updater.condition_on_skill(skill_1_true)
belief_updater.propagate_evidence(('item6', 'true'))
belief_updater.propagate_evidence(('item8', 'true'))
belief_updater.propagate_evidence(('item12', 'false'))
belief_updater.propagate_evidence(('item14', 'false'))
belief_updater.propagate_evidence(('item16', 'false'))
belief_updater.propagate_evidence(('item9', 'true'))
belief_updater.propagate_evidence(('item4', 'true'))
belief_updater.propagate_evidence(('item11', 'true'))
belief_updater.propagate_evidence(('item17', 'true'))
belief_updater.propagate_evidence(('item20', 'true'))
belief_updater.propagate_evidence(('item18', 'false'))
belief_updater.propagate_evidence(('item15', 'false'))
belief_updater.propagate_evidence(('item7', 'false'))
belief_updater.propagate_evidence(('item19', 'false'))
belief_updater.propagate_evidence(('item10', 'false'))
# visualization.pmf_dist("after")
print(scope)

analyzer = LogAnalyzer()
run_entries = analyzer.parse_last_entry()
visualization.skills_dynamics(analyzer.get_pmf_dynamics())

# %%
