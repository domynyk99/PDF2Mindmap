# Third party imports
from dotenv import load_dotenv
from colorama import Fore

# Local application imports
from src.pdf2mindmap.main.lecture_agent import LectureAgent
from src.pdf2mindmap.utils.pdf_converter import PdfConverter
from src.pdf2mindmap.utils.directory_reset import directory_reset
from src.pdf2mindmap.utils.constants import (
    LECTURE_PATH,
    STREAMLIT_HINT
)

def main():
    load_dotenv()

    # 1. Reset all files and directory for clean start
    directory_reset()

    # 2. Convert PDF file and save it in resources
    pdf_converter = PdfConverter(LECTURE_PATH)
    pdf_converter.convert()

    # 3. Call AI Agent workflow
    print("Calling the AI workflow...")
    agent = LectureAgent()
    agent.run()

    # 4. Open MindMap in streamlit hint
    print(Fore.CYAN + STREAMLIT_HINT)

if __name__ == "__main__":
    print("WARNING: To run this project properly use pip install to install the dependencies and the 'summarize' command in the terminal")
    # If you do not want to use the command uncomment the next line
    # main() 