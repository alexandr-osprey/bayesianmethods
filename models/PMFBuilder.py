from pgmpy.models import BayesianNetwork
import networkx as nx
from models.PMFTree import PMFTree
from pydantic import BaseModel
from models.Footprint import Footprint
from pgmpy.factors.discrete import DiscreteFactor

class PMFBuilder(BaseModel):
    full_model: BayesianNetwork
    emf_footprints: list[Footprint]
    skills_edges: list[tuple]

    class Config:
        arbitrary_types_allowed = True 
    
    def build(self) -> PMFTree:
        skills = self._get_skills_nodes()
        footprints = self.emf_footprints
        footprints.sort(key=lambda x: len(x))
        redundant_footprints = []
        for footprint in footprints:
            containing = [c for c in footprints if c != footprint and footprint.issubset(c)]
            if len(containing) > 0:
                redundant_footprints.append(footprint)
        
        footprints = [f for f in footprints if f not in redundant_footprints]
        
        # Step 2: Create a clique graph
        # The nodes are cliques, and edges are weighted by the size of their intersection
        clique_graph = nx.Graph()
        for i, clique1 in enumerate(footprints):
            for j, clique2 in enumerate(footprints):
                if i < j:  # Avoid duplicate edges
                    # Compute the intersection size as the weight
                    intersection = clique1.intersection(clique2)
                    if intersection:
                        clique_graph.add_edge(clique1, clique2, weight=len(intersection), intersection=intersection)
        
        # Step 3: Compute the Maximum Weight Spanning Tree
        st = nx.maximum_spanning_tree(clique_graph)
        cliques_neighbours = {}
        cliques_factors = {}
        cliques = list(frozenset([Footprint(nodes=n) for n in st.nodes]))
        cliques.sort()

        #jt.add_nodes_from([tuple(node) for node in st.nodes])
        cpds_dict = {s: self.full_model.get_cpds(s).to_factor() for s in skills}
        for node in cliques:
            joint = self._get_factors_for_node(node, cpds_dict)
            cliques_factors[node] = joint
        
        junctions = []
        junctions_neighbors = {}
        junctions_factors = {}

        for u, v, data in st.edges(data=True):
            # for vertex of the edge add intersection as neighbor
            intersection = data["intersection"]
            u_neighbours = cliques_neighbours.get(u, [])
            u_neighbours.append(intersection)
            cliques_neighbours[u] = u_neighbours

            v_neighbours = cliques_neighbours.get(v, [])
            v_neighbours.append(intersection)
            cliques_neighbours[v] = v_neighbours

            # for intersections do the same, but separately
            junctions_factors[intersection] = self._get_factors_for_node(intersection, cpds_dict)
            neighbors = junctions_neighbors.get(intersection, [])
            neighbors = neighbors + [u, v]
            junctions_neighbors[intersection] = neighbors
            junctions.append(intersection)

        # assign bigger footprints to the smaller ones
        redundant_footprints_mapping = {}
        for r in redundant_footprints:
            for c in cliques:
                if r.issubset(c):
                    redundant_footprints_mapping[r] = c
                    break


        junctions = list(frozenset(junctions))
        junctions.sort()

        for k in cliques_neighbours.keys():
            cliques_neighbours[k] = frozenset(cliques_neighbours[k])
        
        for k in junctions_neighbors.keys():
            junctions_neighbors[k] = frozenset(junctions_neighbors[k])

        pmf = PMFTree(
            clique_factors=cliques_factors, 
            clique_neighbors=cliques_neighbours, 
            redundant_footprints_mapping=redundant_footprints_mapping,
            junction_factors=junctions_factors, 
            junction_neighbors=junctions_neighbors,
            skills_edges=self.skills_edges)

        return pmf
    
    def _get_skills_nodes(self):
        return [node for node in self.full_model.nodes() if node.startswith('s')]
    
    def _get_factors_for_node(self, node, cpds_dict) -> DiscreteFactor:
        factors = [cpds_dict[e] for e in node]
        joint = factors[0]
        for i in range(1, len(factors)):
            joint = joint * factors[i]
        marginalize_out = list(set(joint.variables) - set(node))
        marginalize_out.sort()
        joint.marginalize(marginalize_out)
        joint.normalize()
        return joint
