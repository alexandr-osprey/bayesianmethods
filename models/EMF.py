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

    def get_footprint_virtual_evidence_dist(self, observable: str, value: str) -> DiscreteFactor:
        if not observable in self.observables:
            raise Exception(f"Observable {observable} not in EMF {self.name}")
        
        left_observables = set(self.observables) - set([observable])
        p_new = self.factor.reduce([(observable, value)], inplace=False)\
            .marginalize(variables=left_observables, inplace=False)

        p_old = self.get_footprint_dist()
        return p_new / p_old
