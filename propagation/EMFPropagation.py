from models.EMFCollection import EMFCollection
from pgmpy.factors.discrete import DiscreteFactor
from models.PMFTree import PMFTree, NodeType
from typed_logging.Logger import Logger
from typed_logging.LogMessage import EMFUpdateMessage
from pydantic import BaseModel
from models.Footprint import Footprint

class EMFPropagation(BaseModel):
    emfs: EMFCollection
    logger: Logger = None

    def model_post_init(self, __context):
        self.logger = Logger()
        return super().model_post_init(__context)

    class Config:
        arbitrary_types_allowed = True 
    
    def propagate(self, pmf: PMFTree) -> None:
        footprints = self.emfs.get_footprints()
        updated_emfs = []
        for footprint in footprints:
            old_emfs = self.emfs.get_emfs_by_footprint(footprint)
            new_footprint_dist = pmf.get_factor(node=footprint, node_type=NodeType.Clique, marginalize=True)
            for emf in old_emfs:
                old_footprint_dist = self._get_emf_footprint_dist(emf, footprint)
                coefs = new_footprint_dist / old_footprint_dist
                updated_emf = emf * coefs
                pure_item = updated_emf.marginalize(variables=footprint, inplace=False).normalize(inplace=False)
                self.logger.info(
                    EMFUpdateMessage(
                        initial_emf=emf.normalize(inplace=False), 
                        footprint=footprint, 
                        #initial_footprint_dist=old_footprint_dist.normalize(inplace=False),
                        #new_footprint_dist=new_footprint_dist.normalize(inplace=False),
                        coefs=coefs.normalize(inplace=False),
                        updated_emf=updated_emf.normalize(inplace=False),
                        pure_item=pure_item))
                updated_emfs.append(updated_emf)
            
        self.emfs.update_emfs(updated_emfs)
    
    def _get_emf_footprint_dist(self, factor: DiscreteFactor, footprint: Footprint) -> DiscreteFactor:
        marginalize_out = [v for v in factor.variables if v not in footprint]
        marginalized = factor.marginalize(marginalize_out, inplace=False)
        return marginalized
