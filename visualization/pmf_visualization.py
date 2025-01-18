
import networkx as nx
import matplotlib.pyplot as plt
from pgmpy.factors.discrete import DiscreteFactor
from pydantic import BaseModel
from models.PMFTree import PMFTree
import numpy as np
import seaborn as sns
import pandas as pd


class PMFVisualization(BaseModel):
    pmf: PMFTree

    def pmf_map(self):
        # Initialize a NetworkX graph
        G = nx.Graph()


        # Add nodes and edges
        dist = self.pmf.get_skills_distributions()
        skills = dist.keys()
        #G.add_nodes_from(nodes)
        G.add_edges_from(self.pmf.skills_edges)


        # Visualize the graph
        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(G)  # Positioning algorithm
        nx.draw(G, pos, with_labels=True, node_size=2000, node_color="lightblue", font_size=10)
        plt.title("Skills")

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
