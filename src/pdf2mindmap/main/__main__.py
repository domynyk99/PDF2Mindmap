# Local application imports
from src.pdf2mindmap.main.lecture_agent import LectureAgent
from src.pdf2mindmap.main.mindmap_creator import MindMapCreator

from src.pdf2mindmap.utils.constants import (
    NODES_EDGES_PATH,
    RESOURCES_DIR,
)
from src.pdf2mindmap.utils.pdf_converter import PdfConverter

def main():
    # 1. Convert PDF file and save it in resources
    pdf_converter = PdfConverter("src/langchain_project/resources/lecture.pdf", RESOURCES_DIR)
    pdf_converter.convert()

    # 2. Call AI Agent workflow
    agent = LectureAgent()
    agent.run()

    # 3. Call Mindmap creator 
    m_map_creator = MindMapCreator(NODES_EDGES_PATH)
    m_map_creator.create_mind_map()

if __name__ == "__main__":
    print("WARNING: To run this project properly use pip install to install the dependencies and the 'summarize' command in the terminal")
    # If you do not want to use the command uncomment the next line
    # main() 