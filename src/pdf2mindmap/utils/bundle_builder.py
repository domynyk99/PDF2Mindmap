# Standard library imports
import os
from pathlib import Path
from typing import List, Tuple

def build_bundles(md_dir: Path, img_dir: Path) -> List[Tuple[str, Path, Path]]:
    """
    Pairs page-XYZ.md with page-XYZ.png by same stem.
    Returns list of (slide_id, md_path, img_path) sorted by slide_id.
    """
    try:
        check_same_files(md_dir, img_dir)
    except RuntimeError as e:
        print("ERROR:", e)
        raise

    bundle: List[Tuple[str, Path, Path]] = [] #List of tuples (page_id, md_path_str, img_path_str)
    
    md_files = sorted(os.listdir(md_dir))
    img_files = sorted(os.listdir(img_dir))

    # Creates a list of tuples of (page_id, md_path, img_path) that later can be used to correctly invoke the llm with
    for md_file, img_file in zip(md_files, img_files):
        page_id = md_file[0:-3]
        md_path = Path(f"{md_dir}/{md_file}")
        img_path = Path(f"{img_dir}/{img_file}")

        bundle.append((page_id, md_path, img_path))

    return bundle    

def check_same_files(md_dir: Path, img_dir: Path) -> None:
    """Checks if images and mds folders have the same data"""
    md_names = []
    img_names = []

    for f_name in os.listdir(md_dir):
        md_names.append(f_name[0:-3])
    
    for f_name in os.listdir(img_dir):
        img_names.append(f_name[0:-4])

    if not md_names or not img_names:
        raise RuntimeError("Image or MD directory is empty")

    if md_names != img_names:
        raise RuntimeError("Image and markdown directory do not have the same (amount, named) files")