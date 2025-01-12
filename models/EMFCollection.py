from pgmpy.factors.discrete import DiscreteFactor
import pandas as pd
import numpy as np
from pydantic import BaseModel
from models.Footprint import Footprint

class EMFCollection(BaseModel):
    skills: list[str]
    emfs: list[DiscreteFactor]
    df: pd.DataFrame = None

    class Config:
        arbitrary_types_allowed = True 

    def model_post_init(self, __context):
        self._set_footprints(self.emfs)

    def _set_footprints(self, emfs: list[DiscreteFactor]) -> None:        
        footprints = []
        items = []
        for emf in emfs:
            footprint =  self._get_footprint(emf)
            item = self._get_item(emf)
            footprints.append(footprint)
            items.append(item)
        
        self.df = pd.DataFrame(data=np.vstack((footprints, emfs)).transpose(), columns=['footprint', 'emf'], index=items)
        self.df.index.name = 'item'
    
    def get_emf_by_item(self, item: str) -> DiscreteFactor: 
        df = self.df
        return df.loc[item]['emf']
    
    def get_footprints(self) -> list[Footprint]:
        footprints = np.unique(self.df['footprint']).tolist()
        return footprints
    
    def get_emfs_by_footprint(self, footprint: Footprint) -> list[DiscreteFactor]:
        return self.df[self.df['footprint'] == footprint]['emf'].tolist()
    
    def normalize(self):
        for row in self.df.iterrows():
            row['factor'].normalize()
    
    def remove_emf_by_item(self, item: str) -> None:
        df = self.df
        self.df = df.drop(index=item)

    def update_emfs(self, emfs: list[DiscreteFactor]) -> None:
        df = self.df
        items = [self._get_item(e) for e in emfs]
        df.loc[items, 'emf'] = emfs
    
    def _get_item(self, emf: DiscreteFactor) -> str:
        return [v for v in emf.variables if v not in self.skills][0]
    
    def _get_footprint(self, emf) -> Footprint:
        return Footprint(nodes=[v for v in emf.variables if v in self.skills])
