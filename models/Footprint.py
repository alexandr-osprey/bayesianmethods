from pydantic import BaseModel, Field
from dataclasses import dataclass

@dataclass(frozen=True)
class Footprint(BaseModel):
    nodes: list[str]
    nodes_set: frozenset[str]

    class Config:
        arbitrary_types_allowed = True 

    def __init__(self, *args, **kwargs):
        nodes = kwargs["nodes"]
        if isinstance(nodes, (frozenset, Footprint)):
            nodes = list(nodes)
            kwargs["nodes"] = nodes
        nodes.sort()
        if "nodes_set" in kwargs:
            raise Exception("nodes set is initialized from nodes")
        
        kwargs["nodes_set"] = frozenset(nodes)
        super().__init__(*args, **kwargs)

    def __hash__(self):
        return hash(self.nodes_set)
    
    def __eq__(self, value):
        if isinstance(value, Footprint):
            return self.nodes == value.nodes
        
        if isinstance(value, list):
            return self.nodes == value
        
        return False
    
    def __repr__(self):
        return f"footprint({repr(self.nodes)})"
    
    def __contains__(self, item):
        return item in self.nodes
    
    def __iter__(self):
        return iter(self.nodes)
    
    def __len__(self):
        return len(self.nodes)
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, Footprint):
            return NotImplemented
        
        return self.nodes < other.nodes
    
    def __lte__(self, other) -> bool:
        if not isinstance(other, Footprint):
            return NotImplemented
        
        return self.nodes <= other.nodes
    
    def __gt__(self, other):
        if not isinstance(other, Footprint):
            return NotImplemented
        
        return self.nodes > other.nodes
    
    def __gte__(self, other):
        if not isinstance(other, Footprint):
            return NotImplemented
        
        return self.nodes >= other.nodes
    
    def issubset(self, other) -> bool:
        if not isinstance(other, Footprint):
            return False
        
        return self.nodes_set.issubset(other.nodes)
    
    def issuperset(self, other) -> bool:
        if not isinstance(other, Footprint):
            return False
        
        return self.nodes.issuperset(other)
    
    def intersection(self, other):
        if not isinstance(other, Footprint):
            return False
        
        return Footprint(nodes=self.nodes_set.intersection(other))
    
    def to_frozenset(self) -> frozenset[str]:
        return self.nodes
