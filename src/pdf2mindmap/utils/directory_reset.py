import os
import shutil

from .constants import (
    SUMMARY_PATH,
    NODES_EDGES_PATH,
    RESOURCES_IMAGES_DIR,
    RESOURCES_JSON_DIR,
    RESOURCES_MARKDOWNS_DIR    
    )


def directory_reset() -> None:
    """
    Reset the working directory structure before the program starts.

    This function removes all files and directories generated during a previous
    program run to ensure a clean state. Specifically, it deletes existing
    summary and data files and recreates the required resource directories
    to prevent conflicts or unexpected behavior caused by leftover artifacts.
    """
    # 1. Delete summary.md and nodes_edges.json in /resources
    files = [SUMMARY_PATH, NODES_EDGES_PATH]
    for file_path in files:
        if os.path.exists(file_path):
            os.remove(file_path)

    # 2. Recreate images, jsons and markdowns directories in /resources
    directories = [RESOURCES_IMAGES_DIR, RESOURCES_JSON_DIR, RESOURCES_MARKDOWNS_DIR]
    for dir_path in directories:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.mkdir(dir_path)