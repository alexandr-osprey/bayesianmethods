from pydantic import BaseModel
from models.Footprint import Footprint
from pgmpy.factors.discrete import DiscreteFactor
import pandas as pd
import numpy as np
from functools import reduce
from enum import Enum


class NodeType(Enum):
    Clique = 1,
    Junction = 2

class PMFTree(BaseModel):
    clique_factors: dict[Footprint, DiscreteFactor]
    clique_neighbors: dict[Footprint, frozenset[Footprint]]
    junction_factors: dict[Footprint, DiscreteFactor]
    junction_neighbors: dict[Footprint, frozenset[Footprint]]
    redundant_footprints_mapping: dict[Footprint, Footprint] = {}
    joint_factor: DiscreteFactor = None
    all_skills_dist: dict[str, np.ndarray] = None
    clique_nodes: frozenset[Footprint] = frozenset()
    clique_elements: frozenset[str] = frozenset()
    skills_edges: list[tuple]
    
    def model_post_init(self, __context):
        self._set_elements()
        return super().model_post_init(__context)

    class Config:
        arbitrary_types_allowed = True

    def set_factor(self, node: Footprint, factor: DiscreteFactor, node_type: NodeType) -> None:
        if node_type == NodeType.Clique:
            self._set_clique_factor(node, factor)
        elif node_type == NodeType.Junction:
            self._set_junction_factor(node, factor)
        else:
            raise Exception("type not handled")
    
    def get_factor(self, node: Footprint, node_type: NodeType, marginalize = False) -> DiscreteFactor:
        if node_type == NodeType.Clique:
            factor = self._get_clique_factor(node)
        elif node_type == NodeType.Junction:
            factor = self._get_junction_factor(node)
        else:
            raise Exception("type not handled")
        
        if marginalize:
            diff = set(factor.variables) - node.nodes_set
            if diff:
                factor = factor.marginalize(variables=diff, inplace=False)
        
        return factor
    
    def get_joint_factor(self) -> DiscreteFactor:
        self._set_joint_factor()
        return self.joint_factor
    
    def get_skills_distributions(self) -> dict:
        self._set_joint_factor()
        return self.all_skills_dist
    
    def get_neighbors(self, node: Footprint, node_type: NodeType, except_for: Footprint = None) -> list[Footprint]:
        if node_type == NodeType.Clique:
            return self._get_clique_neighbors(node, except_for)
        elif node_type == NodeType.Junction:
            return self._get_junction_neighbors(node, except_for)
        raise Exception("type not handled")
    
    def normalize(self):
        for k, v in self.clique_factors.items():
            v.normalize()
        for k, v in self.junction_factors.items():
            v.normalize()
    
    def _set_clique_factor(self, node: Footprint, factor: DiscreteFactor) -> None:
        key = self._get_mapped_node(node)
        
        if key not in self.clique_factors:
            raise Exception(f"{key} not in factors")
        
        old_factor = self.clique_factors[key] 
        if set(old_factor.variables) != set(factor.variables):
            raise Exception(f"sets are different for factors")
        
        self.clique_factors[key] = factor
        self.joint_factor = None
        self.all_skills_dist = None
    
    def _set_junction_factor(self, node: Footprint, factor: DiscreteFactor) -> None:
        if node not in self.junction_factors:
            raise Exception(f"{node} not in factors")
        
        old_factor = self.junction_factors[node] 
        if set(old_factor.variables) != set(factor.variables):
            raise Exception(f"sets are different for factors")
        
        self.junction_factors[node] = factor
    
    def _get_clique_factor(self, node: Footprint) -> DiscreteFactor:
        possible_footprint = self._get_mapped_node(node)
        if possible_footprint in self.clique_factors:
            return self.clique_factors[possible_footprint]
        
        leftover_elements = self.clique_elements - node.nodes_set
        if len(leftover_elements) > 0:
            raise Exception(f"{leftover_elements} not in factors")
        
        self._set_joint_factor()
        factors = [self.joint_factor.loc[f]['factor'] for f in node]
        return reduce(np.multiply, factors)

    def _get_junction_factor(self, node: Footprint) -> DiscreteFactor:
        if node not in self.junction_factors:
            raise Exception(f"{node} not in factors")

        return self.junction_factors[node]

    def _get_mapped_node(self, node: Footprint) -> Footprint:
        if node is None:
            return None
        
        mapped_footprint = node
        if node in self.redundant_footprints_mapping:
            mapped_footprint = self.redundant_footprints_mapping[node]
        
        return mapped_footprint
    
    def _get_clique_neighbors(self, node: Footprint, except_for_junction: Footprint = None) -> list[Footprint]:
        mapped_footprint = self._get_mapped_node(node)
        result = self.clique_neighbors[mapped_footprint]
        if except_for_junction != None:
            result = result - {except_for_junction}
        
        return list(result)
    
    def _get_junction_neighbors(self, node: Footprint, except_for: Footprint = None) -> list[Footprint]:
        mapped_except = self._get_mapped_node(except_for)
        result = self.junction_neighbors[node]
        if mapped_except != None:
            result = result - {mapped_except}
        
        return list(result)
    
    def _set_elements(self):
        self.clique_nodes = frozenset(self.clique_factors.keys())
        elements = []
        for c in self.clique_nodes:
            elements = elements + c.nodes
        self.clique_elements = frozenset(elements)

    def _set_joint_factor(self) -> None:
        if self.joint_factor is not None:
            return
        
        distributions = {}
        for factor in self.clique_factors.values():
            for v in factor.variables:
                marginalize_out = [vv for vv in factor.variables if vv != v]
                marginalized = factor.marginalize(marginalize_out, inplace=False)
                factors: list = distributions.get(v, [])
                factors.append(marginalized)
                distributions[v] = factors
        
        mean_factors = []
        ordered_elements = sorted(self.clique_elements)
        self.all_skills_dist = {}
        for element in ordered_elements:
            factors = distributions[element]
            values = [f.normalize(inplace=False).values for f in factors]
            mean_values = np.mean(values, axis=0)
            std = np.std(values, axis=0)
            for v in std:
                if v > 0.1:
                    raise Exception("PMF does not converge")
            mean_factor = DiscreteFactor(factors[0].variables, factors[0].cardinality, mean_values)
            mean_factors.append(mean_factor)
            self.all_skills_dist[element] = mean_values

        self.joint_factor = reduce(np.multiply, mean_factors)
        self.joint_factor.normalize()
