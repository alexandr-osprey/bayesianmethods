from pydantic import BaseModel
from pgmpy.factors.discrete import DiscreteFactor
from models.Footprint import Footprint
import numpy as np

class EMF(BaseModel):
    factor: DiscreteFactor
    observables: list[str]
    name: str = None
    footprint: Footprint = None

    class Config:
        arbitrary_types_allowed = True 

    def model_post_init(self, __context):
        if self.name == None:
            self.name = self.observables[0]
        self._set_footprint()
        
    def _set_footprint(self) -> None:
        self.footprint = Footprint(nodes=[v for v in self.factor.variables if v not in self.observables])

    def update_factor(self, new_factor: DiscreteFactor) -> None:
        if set(new_factor.variables) - set(self.factor.variables):
            raise Exception(f"For EMF {self.name} new factor has different variables")
        
        self.factor = new_factor
    
    def get_footprint_dist(self) -> DiscreteFactor:
        marginalize_out = [v for v in self.factor.variables if v not in self.footprint]
        marginalized = self.factor.marginalize(marginalize_out, inplace=False)
        return marginalized
    
    def get_observables_dist(self) -> DiscreteFactor:
        observables_factor = self.factor.marginalize(variables=self.footprint, inplace=False).normalize(inplace=False)
        return observables_factor

    def get_virtual_evidence_dist(self, observable: str, value: str) -> DiscreteFactor:
        if not observable in self.observables:
            raise Exception(f"Observable {observable} not in EMF {self.name}")
        
        f = self.factor
        variables = f.variables.copy()
        index = f.state_names[observable].index(value)
        evidence_var_index = f.variables.index(observable)
        variables.pop(evidence_var_index)
        cardinality = np.delete(f.cardinality, evidence_var_index)
        values = np.take(f.values, index, axis=evidence_var_index)
        state_names = f.state_names.copy()
        state_names.pop(observable)
        observable_factor = DiscreteFactor(variables, cardinality=cardinality, values=values, state_names=state_names)

        p_old = self.get_footprint_dist()
        return observable_factor / p_old
