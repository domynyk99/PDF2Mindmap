import os
import json

# Third-party imports
import streamlit as st
from yfiles_graphs_for_streamlit import StreamlitGraphWidget, Node, Edge

# Local application imports
from src.pdf2mindmap.utils.constants import NODES_EDGES_PATH

st.set_page_config(
    page_title="Lecture Mindmap",
    layout="wide"
)

st.markdown("---")
st.title("Lecture Mindmap")

with open(NODES_EDGES_PATH, "r", encoding="utf-8") as f:
    nodes_and_edges = f.read()

# Serialize the string as a dictionary
data = json.loads(nodes_and_edges)

nodes = []
edges = []

for node in data["nodes"]:
    nodes.append(Node(id=node["id"], properties={"label": node["label"]}))
for edge in data["edges"]:    
    edges.append(Edge(start=edge["from"], end=edge["to"])) #, properties={"label": edge["label"]}))

# initialize and render the component
StreamlitGraphWidget(nodes, edges).show()

st.markdown("---")