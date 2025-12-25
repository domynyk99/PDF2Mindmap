# Standard library imports
import os
import shutil
from pathlib import Path

# Third-party imports
import pymupdf
import pymupdf4llm

# Local application imports
from src.pdf2mindmap.utils.constants import RESOURCES_DIR

class PdfConverter():
    def __init__(self, file_path: Path, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.doc = pymupdf.open(file_path)

    def pdf_to_markdown(self):
        """Saves markdowns of every single slide of a PDF and saves them in a folder in the resources directory"""
        markdown_output_dir = self.output_dir / "markdowns"
        self.recreate_directory(markdown_output_dir)

        for page in self.doc:
            md_text = pymupdf4llm.to_markdown(doc=self.doc, pages=[page.number])
            page_number = page.number+1
            page_number_str = f"{page_number:02d}"
            md_file = markdown_output_dir / f"page-{page_number_str}.md"
            md_file.write_text(md_text, encoding="utf-8")  

    def pdf_to_png(self):
        """Saves screenshots of every single slide of a PDF and saves them in a folder in the resources directory"""
        png_output_dir = self.output_dir / "images"
        self.recreate_directory(png_output_dir)

        for page in self.doc:
            pix = page.get_pixmap()  # Renders page to an image
            page_number = page.number+1
            page_number_str = f"{page_number:02d}"
            png_file = png_output_dir / f"page-{page_number_str}.png"
            pix.save(png_file)
    
    def recreate_directory(self, path: Path) -> None:
        """
        Deletes a directory if it exists and recreates it empty.
        """
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)

    def convert(self):
        print("Converting pdf to markdown and pngs...")
        self.pdf_to_markdown()
        self.pdf_to_png()

if __name__ == "__main__":
    pdf_converter = PdfConverter("src/langchain_project/resources/Vorlesung.pdf", RESOURCES_DIR)