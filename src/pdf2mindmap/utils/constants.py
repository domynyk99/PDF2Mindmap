from pathlib import Path

"""This module defines project-level constants."""

LECTURE_PATH = Path("src/pdf2mindmap/resources/lecture.pdf")

RESOURCES_JSON_DIR = Path("src/pdf2mindmap/resources/jsons/")
RESOURCES_IMAGES_DIR = Path("src/pdf2mindmap/resources/images/")
RESOURCES_MARKDOWNS_DIR = Path("src/pdf2mindmap/resources/markdowns/")

SUMMARY_PATH = Path("src/pdf2mindmap/resources/summary.md")
NODES_EDGES_PATH = Path("src/pdf2mindmap/resources/nodes_edges.json")

STREAMLIT_HINT = (
    "\nThe mind map has been generated successfully.\n"
    "To visualize it using the Streamlit app, execute the following command:\n\n"
    "   ---> streamlit run src/pdf2mindmap/main/streamlit_mindmap.py\n"
)