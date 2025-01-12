from models.PMFTree import PMFTree
from models.EMFCollection import EMFCollection
from pgmpy.factors.discrete import DiscreteFactor
from propagation.PMFPropagation import PMFPropagation
from propagation.EMFPropagation import EMFPropagation
from typed_logging.Logger import Logger
from typed_logging.LogMessage import EvidencePropagatedInPMFMessage
from pydantic import BaseModel
import numpy as np

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
        self.emf_propagation = EMFPropagation(emfs=self.emfs)

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
        item = evidence[0]
        emf = self.emfs.get_emf_by_item(item)

        p_new = self._get_p_new(emf, evidence)
        p_old = self._get_p_old(emf, evidence)
        evidence_factor = p_new / p_old

        self.pmf_propagation.propagate(evidence_factor)
        self.emfs.remove_emf_by_item(item)
        self.emf_propagation.propagate(self.pmf)
        self.logger.info(EvidencePropagatedInPMFMessage(initial=initial_pmf, updated=self.pmf.get_skills_distributions()))
        self.logger.end_scope()

    def _get_p_new(self, emf: DiscreteFactor, evidence: tuple) -> DiscreteFactor:
        variables = emf.variables.copy()
        evidence_var_index = emf.variables.index(evidence[0])
        variables.pop(evidence_var_index)
        cardinality = np.delete(emf.cardinality, evidence_var_index)
        values = np.take(emf.values, evidence[1], axis=evidence_var_index)
        factor = DiscreteFactor(variables, cardinality=cardinality, values=values)

        return factor
    
    def _get_p_old(self, emf: DiscreteFactor, evidence: tuple) -> DiscreteFactor:
        marginalized = emf.marginalize([evidence[0]], inplace=False)
        return marginalized
