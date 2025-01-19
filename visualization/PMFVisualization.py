
import networkx as nx
import matplotlib.pyplot as plt
from pgmpy.factors.discrete import DiscreteFactor
from pydantic import BaseModel
from models.PMFTree import PMFTree
import numpy as np
import seaborn as sns
import pandas as pd
import networkx as nx


class PMFVisualization(BaseModel):
    pmf: PMFTree

    def pmf_map(self):
        self._draw_skills_map()
        self._draw_junction_tree()
        plt.show()
    
    def pmf_dist(self, label: str):
        dist = self.pmf.all_skills_dist

        df = pd.DataFrame(data=dist, index=['no', 'yes'])
        df.T.plot(kind="bar", stacked=True, figsize=(8,6), colormap="viridis")

        plt.title('Stacked Bar Chart of Skill Distributions')
        plt.xlabel('Skills')
        plt.ylabel(f'Probability {label}')
        plt.legend(title='States', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()  # Adjust layout to fit labels
        plt.show()
    
    def _draw_skills_map(self):
        G = nx.Graph()
        dist = self.pmf.get_skills_distributions()
        skills = dist.keys()
        #G.add_nodes_from(nodes)
        G.add_edges_from(self.pmf.skills_edges)

        # Visualize the graph
        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(G)  # Positioning algorithm
        nx.draw(G, pos, with_labels=True, node_size=2000, node_color="lightblue", font_size=10)
        plt.title("Skills")
    
    def _draw_junction_tree(self):
        G = nx.Graph()
        junctions = list(self.pmf.junction_factors.keys())
        nodes = list(self.pmf.clique_nodes) + junctions
        edges = []
        for k, neighbors in self.pmf.junction_neighbors.items():
            for n in neighbors:
                edges.append((k, n))
        
        G.add_edges_from(edges)
        G.add_nodes_from(nodes)
        labels = {n: ', '.join(n.nodes) for n in nodes}
        plt.figure(figsize=(8,6))
        pos = nx.spring_layout(G)

        node_colors = []
        for n in G.nodes:
            color = 'lightblue'
            if n in junctions:
                color = 'yellow'
            node_colors.append(color)
        nx.draw(G, pos, with_labels=True, labels=labels, node_size=2000, font_size=10, node_color=node_colors)
        plt.title("Junction tree")
