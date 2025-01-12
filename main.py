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

def print_cpd(cpd):
    backup = TabularCPD._truncate_strtable
    TabularCPD._truncate_strtable = lambda self, x: x
    print(cpd)
    TabularCPD._truncate_strtable = backup

def display_emfs(emfs):
    for emf in emfs:
        print(emf.edges)
        for cpd in emf.get_cpds():
            print_cpd(cpd)

def update_pmf(pmf, all_skills, factor):
    inference = BPM(pmf)
    footprint = [n for n in factor.variables if n in all_skills]
    factor.marginalize(set(factor.variables) - set(footprint))
    print(factor)
    inference.query(['s1', 's2', 's3', 's4'], virtual_evidence=[factor])
    print(inference)
  
def get_skill_edges(model):
    edges = model.edges()
    edges = [e for e in edges if e[1].startswith('s') and e[0].startswith('s')]
    return edges

def get_pmf_emfs():
    db = FullDataBuilder()
    initial_pmf = db.create_initial_pmf()
    all_skills = [str(n) for n in initial_pmf.nodes]
    full_model = db.create_full_model(initial_pmf)
    q_matrix = db.create_q_matrix(full_model)
    emfs = db.create_emfs(full_model, q_matrix)
    emf_collection = EMFCollection(skills=all_skills, emfs=emfs)
    pmf_builder = PMFBuilder(full_model=full_model, emf_footprints=emf_collection.get_footprints())
    pmf = pmf_builder.build()
    return (pmf, emf_collection)

def config_run_dependencies(binder: inject.Binder):
    binder.bind(LoggerConfig, LoggerConfig(mode=LoggerModeEnum.Run))

inject.configure(config_run_dependencies)
pgmpy.config.set_backend('numpy')
pmf, emf_collection = get_pmf_emfs()

logger = Logger()
now = datetime.now()
scope = f"run{now.strftime("%Y%m%dT%H%M%S")}"
logger.start_scope(scope)
belief_updater = BeliefUpdater(pmf=pmf, emfs=emf_collection)
skill_1_true = DiscreteFactor(["s1"], cardinality=[2], values=[0, 1])
belief_updater.condition_on_skill(skill_1_true)
belief_updater.propagate_evidence(('item6', 1))
belief_updater.propagate_evidence(('item8', 1))
belief_updater.propagate_evidence(('item12', 0))
belief_updater.propagate_evidence(('item14', 0))
belief_updater.propagate_evidence(('item16', 0))
belief_updater.propagate_evidence(('item9', 1))
belief_updater.propagate_evidence(('item4', 1))
belief_updater.propagate_evidence(('item11', 1))
belief_updater.propagate_evidence(('item17', 1))
belief_updater.propagate_evidence(('item20', 1))
belief_updater.propagate_evidence(('item18', 0))
belief_updater.propagate_evidence(('item15', 0))
belief_updater.propagate_evidence(('item7', 0))
belief_updater.propagate_evidence(('item19', 0))
belief_updater.propagate_evidence(('item10', 0))
print(scope)
