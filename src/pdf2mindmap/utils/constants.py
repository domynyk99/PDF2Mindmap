from pathlib import Path

"""This module defines project-level constants."""

LECTURE_PATH = Path("src/pdf2mindmap/resources/lecture.pdf")

RESOURCES_DIR = Path("src/pdf2mindmap/resources")
RESOURCES_JSON_DIR = Path("src/pdf2mindmap/resources/jsons/")

SUMMARY_PATH = RESOURCES_DIR / "summary.md"

NODES_EDGES_PATH = Path("src/pdf2mindmap/resources/nodes_edges.json")

MIND_MAP_OUTPUT_DIR = Path("src/pdf2mindmap/resources/mindmap")

STREAMLIT_HINT = (
    "\nThe mind map has been generated successfully.\n"
    "To visualize it using the Streamlit app, execute the following command:\n\n"
    "   ---> streamlit run src/pdf2mindmap/main/streamlit_mindmap.py\n"
)