# Standard library imports
import base64
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

# Third-party imports
from tqdm import tqdm
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# Local application imports
from src.pdf2mindmap.utils.page_grouper import PageGrouper
from src.pdf2mindmap.utils.bundle_builder import build_bundles
from src.pdf2mindmap.utils.constants import (
    NODES_EDGES_PATH,
    RESOURCES_DIR,
    RESOURCES_JSON_DIR,
    SUMMARY_PATH
)
from src.pdf2mindmap.utils.prompts import (
    SINGLE_SLIDE_EXTRACTOR_PROMPT,
    MULTIPLE_SLIDE_EXTRACTOR_PROMPT,
    MINDMAP_PROMPT,
    SUMMARY_PROMPT,
    SYSTEM_PROMPT,
)

class LectureAgent():
    """
    This class represents the AI agents workflow.

    1. grouped_slide_summary(): The agent creates summaries for grouped slides
    2. summarize(): Then it summarizes all the single slide summaries in one markdown file
    3. summary_to_mind_map(): At last it creates a json file containing the nodes and edges for the mindmap
    """
    def __init__(self) -> None:
        self.summary_model = init_chat_model("gpt-4.1-mini-2025-04-14", temperature = 0.5)
        self.directory = RESOURCES_DIR
        self.bundles = build_bundles(self.directory / "markdowns", self.directory / "images")
        load_dotenv()

    def run(self) -> None:
        #self.single_slide_summary() 
        self.grouped_slides_summary()
        print("Generating Markdown Summary of your lecture...")
        self.summarize()
        print("Generating the nodes and edges of your mindmap...")
        self.summary_to_mind_map()

    def grouped_slides_summary(self):
        """
        Generate summarized JSON outputs for groups of semantically similar slides.

        This method performs the following steps:

        1. Ensures that the RESOURCES_JSON_DIR directory is reset by deleting any
        existing directory and recreating it.
        2. Uses :class: PageGrouper to cluster slides into groups of semantically
        related pages using HDBSCAN.
        3. For each slide group, constructs a multimodal prompt consisting of:
            - the combined markdown content of all slides in the group
            - the corresponding slide images encoded as base64 URLs
        4. Invokes the summary model with the generated prompt.
        5. Writes the resulting structured summaries to individual JSON files
        in RESOURCES_JSON_DIR.

        Each output file contains the summarized content for one slide group.

        :return: None
        """

        # 1. Reset resources/jsons directory
        if Path(RESOURCES_JSON_DIR).exists():
                shutil.rmtree(RESOURCES_JSON_DIR)
        Path(RESOURCES_JSON_DIR).mkdir(parents=True, exist_ok=True)

        # 2. Use PageGrouper to group slides into semantically related pages
        page_grouper = PageGrouper()
        page_grouper.run()
        groups = page_grouper.groups

        # 3. For each slide group construct prompt
        for group, pages_list in tqdm(groups.items(), desc="Generating JSON summaries"):
            messages = [
                {"role": "user", "content": [
                ]}
            ]

            group_prompt = MULTIPLE_SLIDE_EXTRACTOR_PROMPT
            image_prompts = []
            for page in pages_list:
                slide_id, md_path, img_path = self.bundles[page-1]
                md_text = self._load_text(md_path)

                single_slide_text_prompt = f"\n\nSLIDE_ID: {slide_id}\nMARKDOWN:\n{md_text}"
                group_prompt += single_slide_text_prompt
                
                image_dict = {"type": "image_url", "image_url": {"url": self._png_to_base64_url(img_path)}}
                image_prompts.append(image_dict)
            
            text_dict = {"type": "text", "text": group_prompt}
            messages[0]["content"].append(text_dict)
            for prompt in image_prompts:
                messages[0]["content"].append(prompt)

            # 4. Invoke model with created prompt
            response = self.summary_model.invoke(messages)

            # Write structured response to JSON files in resources/jsons
            data = json.loads(response.content)
            all_notes = []
            all_notes.append(data)
            with open(RESOURCES_JSON_DIR / f"{slide_id}.json", "w", encoding="utf-8") as f:
                json.dump(all_notes, f, ensure_ascii=False, indent=2)

    def summarize(self):
        """
        Generate a consolidated Markdown summary for the entire lecture.

        This method reads all JSON summary files located in RESOURCES_JSON_DIR,
        each representing a summarized slide group, and combines their contents
        into a single prompt. The prompt is then passed to the summary model to
        generate a comprehensive Markdown summary of the full lecture.

        The resulting summary is written to SUMMARY_PATH.

        :return: None
        """
        slides = []
        
        # Loop through resources/jsons, convert JSONs to dictionaries and append them to the slides list
        directory = RESOURCES_JSON_DIR
        for filename in os.listdir(directory):
            with open(os.path.join(directory, filename)) as json_slide: 
                slide = json.load(json_slide)
            slides.append(slide)
        
        # Construct a summarization prompt with the slides list
        messages = [
            {
                "role": "system",
                "content": SUMMARY_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {"type": "text",
                        "text": (
                            "Below is a list of JSON objects. "
                            "Each object represents a summary of a semantically related group of lecture slides.\n\n"
                            "Use this information to generate a coherent, well-structured summary of the entire lecture.\n\n"
                            f"{json.dumps(slides, ensure_ascii=False, indent=2)}")
                    }
                ]
            }
        ]
        # invoke the model with the message
        response = self.summary_model.invoke(messages)
    
        # Store response in resources/summary.md 
        with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
            f.write(response.content)
    
    def summary_to_mind_map(self):
        """
        Generate a mind map representation from the lecture summary.

        This method reads the consolidated lecture summary from SUMMARY_PATH
        and uses it to construct a prompt for the mind map generation model.
        The model response is expected to describe nodes and edges (including labels)
        that represent the conceptual structure of the lecture.

        The generated nodes and edges are written as a JSON file to
        NODES_EDGES_PATH and can be used later to build a visual mind map.

        :return: None
        """
        with open(SUMMARY_PATH, "r") as f:
            md_summary = f.read()

        # Construct a prompt with the resources/summary.md
        messages = [
            {
                "role": "system",
                "content": MINDMAP_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": md_summary
                    }
                ]
            }
        ]

        # Invoke the model and store the node_edges.json in resources directory
        response = self.summary_model.invoke(messages)
        with open(NODES_EDGES_PATH, "w", encoding="utf-8") as f:
            f.write(response.content)

    def _load_text(self, path: Path) -> str:
        """
        Load the textual content of a markdown file.

        This helper method reads a slide's markdown representation and returns
        its contents as a plain string. The returned text is used as input for downstream
        processing (e.g., building prompts for grouped_slides_summary and
        single_slide_summary).

        :param path: Path to the markdown file.
        :type path: pathlib.Path
        :return: Markdown file contents as a single string.
        :rtype: str
        """
        return path.read_text(encoding="utf-8", errors="ignore")

    def _png_to_base64_url(self, png_path: Path) -> str:
        """
        Encode a PNG image as a base64 data URL.

        This helper method reads a PNG image from disk, encodes it in base64,
        and returns a data URL string that can be embedded directly into
        multimodal prompts (e.g., for grouped_slides_summary or
        single_slide_summary).

        :param png_path: Path to the PNG image file.
        :type png_path: pathlib.Path
        :return: Base64-encoded PNG image as a data URL.
        :rtype: str
        """
        data = png_path.read_bytes()
        b64 = base64.b64encode(data).decode()
        return f"data:image/png;base64,{b64}"

    def single_slide_summary(self):
        """
        Generate JSON summaries for individual slides using a multimodal prompt.

        This method is functionally similar to :meth:`grouped_slides_summary`, but
        processes each slide independently instead of grouping them. It is currently
        not used by default because generating summaries per slide results in higher
        token usage and increased cost.

        The method performs the following steps:

        1. Ensures that the RESOURCES_JSON_DIR directory is reset by deleting any
        existing directory and recreating it.
        2. Iterates over all slide bundles.
        3. For each slide, constructs a multimodal prompt containing:
            - the slide's markdown content
            - the corresponding slide image encoded as a base64 URL
        4. Invokes the summary model for each slide individually.
        5. Writes one JSON summary file per slide to RESOURCES_JSON_DIR.

        This method is kept for experimentation or comparison with grouped summaries.

        :return: None
        """
        
        # Reset resources/jsons directory
        if Path(RESOURCES_JSON_DIR).exists():
                shutil.rmtree(RESOURCES_JSON_DIR)
        Path(RESOURCES_JSON_DIR).mkdir(parents=True, exist_ok=True)
        
        # Create 
        for slide_id, md_path, img_path in self.bundles:
            md_text = self._load_text(md_path)

            messages = [
                {"role": "user", "content": [
                    {"type": "text", "text": f"SLIDE_ID: {slide_id}\n\nMARKDOWN:\n{md_text}\n\n{SINGLE_SLIDE_EXTRACTOR_PROMPT}"},
                    {"type": "image_url", "image_url": {"url": self._png_to_base64_url(img_path)}},
                ]}
            ]

            response = self.summary_model.invoke(messages)

            print(response.usage_metadata)
            data = json.loads(response.content)

            all_notes = []

            all_notes.append(data)

            with open(RESOURCES_JSON_DIR / f"{slide_id}.json", "w", encoding="utf-8") as f:
                json.dump(all_notes, f, ensure_ascii=False, indent=2)