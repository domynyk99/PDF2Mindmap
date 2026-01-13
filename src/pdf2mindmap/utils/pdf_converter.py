# Standard library imports
import os
import re
import shutil
from pathlib import Path
from pprint import pprint
from collections import Counter

# Third-party imports
import pymupdf
import pymupdf.layout
import pymupdf4llm

# Local application imports
from src.pdf2mindmap.utils.constants import (
    LECTURE_PATH,
    RESOURCES_MARKDOWNS_DIR,
    RESOURCES_IMAGES_DIR
    )

class PdfConverter():
    def __init__(self, file_path: Path) -> None:
        self.doc = pymupdf.open(file_path)

    def pdf_to_markdown(self):
        """Saves markdowns of every single slide of a PDF and saves them in a folder in the resources directory"""
        markdown_output_dir = RESOURCES_MARKDOWNS_DIR

        md_pages = {}

        # Converting single slides to markdown text with initial cleaning of md_text
        for page in self.doc:
            md_text = pymupdf4llm.to_markdown(doc=self.doc,
                                              pages=[page.number],
                                              footer=False,
                                              header=False,
                                              use_ocr=False,
                                              write_images=False,
                                              force_text=True
                                              )
            md_text = self._clean_markdown(md_text)
            page_number = page.number+1
            md_pages[page_number] = md_text

        # Dedup of all markdown pages
        md_pages = self.dedup(md_pages)

        # Writing preprocessed markdown pages to .md files in output directory
        for page_num, md in md_pages.items():
            page_num_str = f"{page_num:02d}"

            md_file = markdown_output_dir / f"page-{page_num_str}.md"
            md_file.write_text(md, encoding="utf-8")

    def pdf_to_png(self):
        """Saves screenshots of every single slide of a PDF and saves them in a folder in the resources directory"""
        png_output_dir = RESOURCES_IMAGES_DIR

        for page in self.doc:
            pix = page.get_pixmap()  # Renders page to an image
            page_number = page.number+1
            page_number_str = f"{page_number:02d}"
            png_file = png_output_dir / f"page-{page_number_str}.png"
            pix.save(png_file)
    
    def convert(self):
        print("Converting pdf to markdown and pngs...")
        self.pdf_to_markdown()
        self.pdf_to_png()

    # --- Only helper functions from here on ---

    def _clean_markdown(self, md_text: str) -> str:
        """Function to clean Markdown output by removing PyMuPDF “picture intentionally omitted” placeholders, reducing noise and token usage in Markdown generated from PDF slides."""
        # REGEX Constants used to clean the pymupdf4llm to_markdown() output
        RE_PICTURE_PLACEHOLDER = re.compile(
            r'^\*\*==>\s*picture\s*\[[^\]]*\]\s*intentionally omitted\s*<==\*\*\s*$',
            re.IGNORECASE | re.MULTILINE
        )
        RE_BR = re.compile(r'\s*<br>\s*', re.IGNORECASE) # HTML breaks
        RE_MULTI_SPACE = re.compile(r'[ \t]{2,}') # 
        RE_MULTI_NL = re.compile(r'\n{3,}') # New lines


        # 1) Remove PyMuPDF "picture intentionally omitted" placeholder lines
        md_text = RE_PICTURE_PLACEHOLDER.sub("", md_text)

        # 2) Replace HTML <br> tags with newline characters
        md_text = RE_BR.sub("\n", md_text)

        # 3) Remove trailing whitespace from each line
        md_text = "\n".join(line.rstrip() for line in md_text.splitlines())

        # 4) Normalize multiple spaces within lines (preserve line breaks)
        md_text = "\n".join(RE_MULTI_SPACE.sub(" ", line) for line in md_text.splitlines())

        # 5) Collapse excessive blank lines and ensure a single trailing newline
        md_text = RE_MULTI_NL.sub("\n\n", md_text).strip() + "\n"

        # Matches lines that contain at least one alphanumeric character
        RE_HAS_TEXT = re.compile(r'[A-Za-z0-9]')
        kept_lines = []      

        # Filter out empty or non-informative lines (e.g. decoration-only lines)
        for line in md_text.splitlines():
            if RE_HAS_TEXT.search(line): #Returns match object or None
                kept_lines.append(line)
        
        md_text = "\n".join(kept_lines)

        # Split bullet points that were incorrectly merged into a single line
        RE_MULTIPLE_BULLETPOINTS_SAME_LINE = re.compile(r'\s•\s')
        md_text = RE_MULTIPLE_BULLETPOINTS_SAME_LINE.sub('\n• ', md_text)

        return md_text

    def dedup(self, md_pages: dict[int, str], threshold: float = 0.5, top_n: int = 6, bottom_n: int = 6):
        """
        Removes lines that repeat across many pages (headers/footers).
        threshold=0.7 => remove if present on >=70% pages (normalized).
        top_n/bottom_n => only consider first/last N lines as boilerplate candidates.
        Returns a dictionary[page_number, md_text] indexed by paged number and containing the cleaned markdown text
        """
        page_items = sorted(md_pages.items())  # stabile Reihenfolge
        n_pages = max(1, len(page_items))

        # collect candidates possibly containing repeated lines
        per_page_norm_sets = {}
        for page_no, md in page_items:
            lines = md.splitlines()
            candidates = lines[:top_n] + (lines[-bottom_n:] if bottom_n > 0 else [])
            norm_set = {self._normalize_line(l) for l in candidates} # candidates are normalized using the normalize_line() function
            norm_set.discard("")
            per_page_norm_sets[page_no] = norm_set

        # count how often each line occurs
        counter = Counter()
        for norm_set in per_page_norm_sets.values():
            counter.update(norm_set)

        common_norm_lines = {
            line for line, c in counter.items()
            if c / n_pages >= threshold and len(line) > 2
        }

        # remove repeated boilerplate lines from each page
        cleaned_pages = {}
        removed_per_page = {}

        for page_no, md in page_items:
            kept = []
            removed = []
            for line in md.splitlines():
                if self._normalize_line(line) in common_norm_lines:
                    removed.append(line)
                else:
                    kept.append(line)
            cleaned_pages[page_no] = "\n".join(kept).strip() + "\n" # rebuild cleaned markdown page
            removed_per_page[page_no] = removed # keep track of removed lines for debugging / analysis

        # --- Print statements for debugging / analysis ---
        # print("Per page norm sets:")
        # pprint(per_page_norm_sets)
        # print("Common norm lines:")
        # pprint(common_norm_lines)
        # print("Cleaned pages:")
        # pprint(cleaned_pages)
        # print("Removed per page:")
        # pprint(removed_per_page)

        return cleaned_pages

    def _normalize_line(self, line: str) -> str:
        line = line.strip()
        if not line:
            return ""
        line = line.lower()
        # neutralise numbers (page_numbers etc.)
        line = re.sub(r'\b\d+\b', '%', line)
        # eliminating 
        line = re.sub(r'[#*-]', '', line)
        # normalizing whitespace 
        line = re.sub(r'\s+', ' ', line)
        # eliminate decorative characters
        line = re.sub(r'[•·●▪■◆]+', '', line).strip()
        return line

if __name__ == "__main__":
    pdf_converter = PdfConverter(LECTURE_PATH)
    pdf_converter.convert()