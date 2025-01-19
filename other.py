
# %%
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Wedge

# Define the graph
G = nx.Graph()
G.add_nodes_from(['Node1', 'Node2', 'Node3'])
G.add_edges_from([('Node1', 'Node2'), ('Node2', 'Node3')])

# Define elements and their colors
element_colors = {
    's1': 'red',    # Red for s1
    's2': 'green',  # Green for s2
    's3': 'blue'    # Blue for s3
}

# Define elements in each node
node_elements = {
    'Node1': ['s1', 's2', 's3'],  # Node1 has s1, s2, s3
    'Node2': ['s2', 's3'],        # Node2 has s2, s3
    'Node3': ['s1', 's3']         # Node3 has s1, s3
}

# Node positions
pos = nx.spring_layout(G)

# Draw the graph edges
plt.figure(figsize=(8, 6))
nx.draw_networkx_edges(G, pos, alpha=0.5)

# Draw nodes with gradient colors
ax = plt.gca()
for node, elements in node_elements.items():
    x, y = pos[node]
    num_elements = len(elements)
    angle_per_element = 360 / num_elements  # Divide node into equal segments
    
    for i, element in enumerate(elements):
        # Start and end angles for the segment
        start_angle = i * angle_per_element
        end_angle = (i + 1) * angle_per_element
        
        # Add a wedge for each element
        wedge = Wedge(center=(x, y), r=0.1, theta1=start_angle, theta2=end_angle, color=element_colors[element])
        ax.add_patch(wedge)

# Add labels
nx.draw_networkx_labels(G, pos)

# Customize and show the plot
plt.axis('off')
plt.title("Nodes with Gradient Representing Elements")
plt.show()

# %%
