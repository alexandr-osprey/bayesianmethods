from models.EMFCollection import EMFCollection
from pgmpy.factors.discrete import DiscreteFactor
from models.PMFTree import PMFTree, NodeType
from typed_logging.Logger import Logger
from typed_logging.LogMessage import EMFUpdateMessage
from pydantic import BaseModel
from models.Footprint import Footprint

class EMFPropagation(BaseModel):
    emf_collection: EMFCollection
    logger: Logger = None

    def model_post_init(self, __context):
        self.logger = Logger()
        return super().model_post_init(__context)

    class Config:
        arbitrary_types_allowed = True 
    
    def propagate(self, pmf: PMFTree) -> None:
        footprints = self.emf_collection.get_footprints()
        for footprint in footprints:
            old_emfs = self.emf_collection.get_emfs_by_footprint(footprint)
            new_footprint_dist = pmf.get_factor(node=footprint, node_type=NodeType.Clique, marginalize=True)
            for emf in old_emfs:
                old_footprint_dist = emf.get_footprint_dist()
                #skills_only = old_footprint_dist.normalize(inplace=False)
                coefs = new_footprint_dist / old_footprint_dist
                updated_emf_factor = emf.factor * coefs
                emf.update_factor(updated_emf_factor)
                self.logger.info(
                    EMFUpdateMessage(
                        initial_emf=emf.factor.normalize(inplace=False), 
                        footprint=footprint, 
                        #initial_footprint_dist=old_footprint_dist.normalize(inplace=False),
                        #new_footprint_dist=new_footprint_dist.normalize(inplace=False),
                        coefs=coefs.normalize(inplace=False),
                        updated_emf_factor=updated_emf_factor.normalize(inplace=False),
                        pure_observables=emf.get_observables_dist()))
