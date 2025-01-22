from pgmpy.factors.discrete import DiscreteFactor
import pandas as pd
import numpy as np
from pydantic import BaseModel
from models.Footprint import Footprint
from models.EMF import EMF

class EMFCollection(BaseModel):
    emfs: list[EMF]

    class Config:
        arbitrary_types_allowed = True

    def get_emf_by_name(self, name: str) -> EMF: 
        emf = [e for e in self.emfs if e.name == name]
        if not emf:
            raise Exception(f"Could not find EMF {name}")
        
        return emf[0]
    
    def get_footprints(self) -> set[Footprint]:
        return set([emf.footprint for emf in self.emfs])
    
    def get_emfs_by_footprint(self, footprint: Footprint) -> list[EMF]:
        return [emf for emf in self.emfs if emf.footprint == footprint]
    
    def remove_emf_by_name(self, name: str) -> None:
        self.emfs = [emf for emf in self.emfs if emf.name != name]
