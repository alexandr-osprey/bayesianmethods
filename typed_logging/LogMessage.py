import pandas as pd
from pgmpy.factors.discrete import DiscreteFactor
from typed_logging.Enums import LogEventEnum
from pydantic import BaseModel
from models.Footprint import Footprint
from typing import Union
import numpy as np
from models.PMFTree import NodeType as PMFNodeType

class LogMessage(BaseModel):
    log_event: LogEventEnum

    class Config:
        arbitrary_types_allowed = True 

class EvidenceCalulatedMessage(LogMessage):
    log_event: LogEventEnum = LogEventEnum.EvidenceCalculated
    emf_initial: DiscreteFactor
    new_factor: DiscreteFactor
    delta: DiscreteFactor = None

    def model_post_init(self, __context):
        self.delta = self.new_factor  + (-1 * self.emf_initial)
        return super().model_post_init(__context)

class EMFUpdateMessage(LogMessage):
    initial_emf: DiscreteFactor
    footprint: list
    #initial_footprint_dist: DiscreteFactor
    #new_footprint_dist: DiscreteFactor
    coefs: DiscreteFactor
    updated_emf_factor: DiscreteFactor
    pure_observables: DiscreteFactor
    log_event: LogEventEnum = LogEventEnum.EMFUpdate
    delta: DiscreteFactor = None

    def model_post_init(self, __context):
        self.delta = self.updated_emf_factor + (-1 * self.initial_emf)
        return super().model_post_init(__context)

class PMFNodeUpdatedMessage(LogMessage):
    def __init__(self, *args, **kwargs):
        node_type = kwargs["node_type"]
        if isinstance(node_type, str):
            node_type = PMFNodeType[node_type]
            kwargs["node_type"] = node_type
        
        super().__init__(*args, **kwargs)

    log_event: LogEventEnum = LogEventEnum.PMFNodeUpdated
    node_type: PMFNodeType
    element: Footprint
    evidence: DiscreteFactor
    old_factor: DiscreteFactor
    neighbors: list[Footprint]
    updated_factor: DiscreteFactor
    message: DiscreteFactor
    delta: DiscreteFactor = None

    def model_post_init(self, __context):
        self.delta = self.updated_factor + (-1 * self.old_factor)
        return super().model_post_init(__context)

class EvidencePropagatedInPMFMessage(LogMessage):
    log_event: LogEventEnum = LogEventEnum.UpdatedPMF
    initial: list[DiscreteFactor]
    updated: list[DiscreteFactor]
    delta: list[DiscreteFactor] = None

    def model_post_init(self, __context):
        self.delta = []
        for k in range(len(self.updated)):
            v2 = self.updated[k]
            v1 = self.initial[k]
            self.delta.append(v2 + (v1 * -1))
        return super().model_post_init(__context)
