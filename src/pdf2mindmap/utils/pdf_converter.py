# Standard library imports
import os
from pathlib import Path

# Third-party imports
import pymupdf
import pymupdf4llm

# Local application imports
from src.pdf2mindmap.utils.constants import RESOURCES_DIR

class PdfConverter():
    def __init__(self, file_path: str, output_dir: str) -> None:
        self.output_dir = output_dir
        self.doc = pymupdf.open(file_path)

    def pdf_to_markdown(self):
        """Saves markdowns of every single slide of a PDF and saves them in a folder in the resources directory"""
        markdown_output_dir = os.path.join(self.output_dir, "markdowns")
        self.check_directory(markdown_output_dir)

        for page in self.doc:
            md_text = pymupdf4llm.to_markdown(doc=self.doc, pages=[page.number])
            page_number = page.number+1
            page_number_str = f"{page_number:02d}"
            Path(f"{markdown_output_dir}/page-{page_number_str}.md").write_text(md_text, encoding="utf-8")  

    def pdf_to_png(self):
        """Saves screenshots of every single slide of a PDF and saves them in a folder in the resources directory"""
        png_output_dir = os.path.join(self.output_dir, "images")
        print(png_output_dir)
        self.check_directory(png_output_dir)

        for page in self.doc:
            pix = page.get_pixmap()  # Renders page to an image
            page_number = page.number+1
            page_number_str = f"{page_number:02d}"
            pix.save(f"{png_output_dir}/page-{page_number_str}.png")
    
    def check_directory(self, directory: str) -> None:
        if not os.path.exists(directory):
            print(f"Creating a directory in: {directory}")
            os.mkdir(directory)
        else:
            print(f"Directory exists {directory}")

    def convert(self):
        print("Converting pdf to markdown and pngs...")
        self.pdf_to_markdown()
        self.pdf_to_png()

if __name__ == "__main__":
    pdf_converter = PdfConverter("src/langchain_project/resources/Vorlesung.pdf", RESOURCES_DIR)