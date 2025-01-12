from pgmpy.factors.discrete import DiscreteFactor
import numpy as np
from models.PMFTree import PMFTree, NodeType
from typed_logging.Logger import Logger
from typed_logging.LogMessage import PMFNodeUpdatedMessage
from models.Footprint import Footprint
from pydantic import BaseModel

class PMFPropagation(BaseModel):
    pmf: PMFTree
    logger: Logger = None

    def model_post_init(self, __context):
        self.logger = Logger()
        return super().model_post_init(__context)

    class Config:
        arbitrary_types_allowed = True
    
    def propagate(self, evidence: DiscreteFactor) -> None:
        self._propagate_recursive(element=Footprint(nodes=evidence.variables), evidence=evidence, source_element=None, node_type=NodeType.Clique)

    def _propagate_recursive(self, element: Footprint, evidence: DiscreteFactor,  node_type: NodeType, source_element: Footprint) -> None:
        pmf = self.pmf

        old_factor = pmf.get_factor(node=element, node_type=node_type)
        neighbors = pmf.get_neighbors(node=element, node_type=node_type, except_for=source_element)
        if node_type == NodeType.Junction:
            marginalize_out = [e for e in evidence.variables if e not in element]
            updated_factor = evidence.marginalize(marginalize_out, inplace=False)
            message = updated_factor / old_factor
            node_type_to_pass = NodeType.Clique
        elif node_type == NodeType.Clique:
            updated_factor = old_factor * evidence
            message = updated_factor
            node_type_to_pass = NodeType.Junction
        else:
            raise Exception("type not handled")

        pmf.set_factor(node=element, factor=updated_factor, node_type=node_type)
        self.logger.info(
            PMFNodeUpdatedMessage(
                element=element,
                evidence=evidence.normalize(inplace=False),
                node_type=node_type,
                old_factor=old_factor.normalize(inplace=False),
                neighbors=neighbors,
                message=message.normalize(inplace=False),
                updated_factor=updated_factor.normalize(inplace=False)))
        
        for n in neighbors:
            self._propagate_recursive(element=n, evidence=message, source_element=element, node_type=node_type_to_pass)

        return
