from models.PMFTree import PMFTree
from models.EMFCollection import EMFCollection
from pgmpy.factors.discrete import DiscreteFactor
from propagation.PMFPropagation import PMFPropagation
from propagation.EMFPropagation import EMFPropagation
from typed_logging.Logger import Logger
from typed_logging.LogMessage import EvidencePropagatedInPMFMessage
from pydantic import BaseModel

class BeliefUpdater(BaseModel):
    pmf: PMFTree
    emfs: EMFCollection
    pmf_propagation: PMFPropagation = None
    emf_propagation: EMFPropagation = None
    logger: Logger = None

    class Config:
        arbitrary_types_allowed = True 
    
    def model_post_init(self, __context):
        self.logger = Logger()
        self.pmf_propagation = PMFPropagation(pmf=self.pmf)
        self.emf_propagation = EMFPropagation(emf_collection=self.emfs)

    def condition_on_skill(self, evidence_factor: DiscreteFactor) -> None:
        self.logger.start_scope(f"condition_on_{evidence_factor.variables}")
        initial_pmf = self.pmf.get_skills_distributions()
        self.pmf_propagation.propagate(evidence_factor)
        self.emf_propagation.propagate(self.pmf)
        self.logger.info(EvidencePropagatedInPMFMessage(initial=initial_pmf, updated=self.pmf.get_skills_distributions()))
        self.logger.end_scope()

    def propagate_evidence(self, evidence: tuple) -> None:
        self.logger.start_scope(evidence)
        initial_pmf = self.pmf.get_skills_distributions()
        name = evidence[0]
        emf = self.emfs.get_emf_by_name(name)

        evidence_factor = emf.get_footprint_virtual_evidence_dist(evidence[0], evidence[1])

        self.pmf_propagation.propagate(evidence_factor)
        self.emfs.remove_emf_by_name(name)
        self.emf_propagation.propagate(self.pmf)
        self.logger.info(EvidencePropagatedInPMFMessage(initial=initial_pmf, updated=self.pmf.get_skills_distributions()))
        self.logger.end_scope()
