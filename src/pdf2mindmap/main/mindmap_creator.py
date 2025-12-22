# Standard library imports
import json
import os

# Third-party imports
from graphviz import Digraph

# Local application imports
from src.pdf2mindmap.utils.constants import (
    MIND_MAP_OUTPUT_DIR,
    NODES_EDGES_PATH,
)

class MindMapCreator():
    def __init__(self, json_path: str):
        self.json_path = json_path
        directory = MIND_MAP_OUTPUT_DIR
        self.check_directory(directory) 
        self.dot = Digraph(format='pdf', directory=directory)

    def create_mind_map(self):
        """
        Loads the json file containing the nodes and edges of the mind map and renders it as a pdf
        """
        with open(self.json_path, "r", encoding="utf-8") as f:
            nodes_and_edges = f.read()

        # Serialize the string as a dictionary
        data = json.loads(nodes_and_edges)

        for node in data["nodes"]:
            self.dot.node(name=node["id"], label=node["label"])
        for edge in data["edges"]:    
            self.dot.edge(edge["from"], edge["to"], label=edge["label"])

        self.dot.render("mindmap", view=True)

    def check_directory(self, directory: str) -> None:
        """Checks if a given directory exists and if not it creates the directory"""
        if not os.path.exists(directory):
            print(f"Creating a directory in: {directory}")
            os.mkdir(directory)
        else:
            print(f"Directory exists {directory}")

if __name__ == "__main__":
    json_path = NODES_EDGES_PATH
    m_map_creator = MindMapCreator(json_path)
    m_map_creator.create_mind_map()