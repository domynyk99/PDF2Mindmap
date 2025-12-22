# Standard library imports
import base64
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

# Third-party imports
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

# Local application imports
from src.pdf2mindmap.utils.bundle_builder import build_bundles
from src.pdf2mindmap.utils.constants import (
    NODES_EDGES_PATH,
    RESOURCES_DIR,
    RESOURCES_JSON_DIR,
)
from src.pdf2mindmap.utils.prompts import (
    EXTRACTOR_PROMPT,
    MINDMAP_PROMPT,
    SUMMARY_PROMPT,
    SYSTEM_PROMPT,
)

class LectureAgent():
    """
    This class represents the AI agents workflow.

    1. single_slide_summary(): The agent creates summaries for every single slide
    2. summarize(): Then it summarizes all the single slide summaries in one markdown file
    3. summary_to_mind_map(): At last it creates a json file containing the nodes and edges for the mindmap
    """
    def __init__(self) -> None:
        self.model = init_chat_model("gpt-4.1-mini-2025-04-14", temperature = 0.5)
        # self.agent = create_agent(
        #     model=self.model,
        #     system_prompt=SYSTEM_PROMPT,
        #     response_format=ResponseFormat
        #     )
        self.directory = RESOURCES_DIR
        self.bundles = build_bundles(f"{self.directory}/markdowns", f"{self.directory}/images")
        load_dotenv()

    def single_slide_summary(self):
        """Creates compact notes of a single slide and safes it in a JSON"""
        
        if Path(RESOURCES_JSON_DIR).exists():
                shutil.rmtree(RESOURCES_JSON_DIR)
        Path(RESOURCES_JSON_DIR).mkdir(parents=True, exist_ok=True)
        
        for slide_id, md_path, img_path in self.bundles:
            md_text = self._load_text(md_path)

            messages = [
                {"role": "user", "content": [
                    {"type": "text", "text": f"SLIDE_ID: {slide_id}\n\nMARKDOWN:\n{md_text}\n\n{EXTRACTOR_PROMPT}"},
                    {"type": "image_url", "image_url": {"url": self._png_to_base64_url(img_path)}},
                ]}
            ]

            response = self.model.invoke(messages)

            print(response.usage_metadata)
            data = json.loads(response.content)

            all_notes = []

            all_notes.append(data)

            with open(RESOURCES_JSON_DIR + f"{slide_id}.json", "w", encoding="utf-8") as f:
                json.dump(all_notes, f, ensure_ascii=False, indent=2)

    def summarize(self):
        """Summarizes the JSONs to a markdown summary about the lecture"""
        slides = []
        
        # Loop through resources/jsons directory, convert them to dictionaries and append them to pages list
        directory = RESOURCES_JSON_DIR
        for filename in os.listdir(directory):
            with open(os.path.join(directory, filename)) as json_slide: 
                slide = json.load(json_slide)
            slides.append(slide)
        
        # combine a new prewritten prompt and dictionary to a message list
        messages = [
            {
                "role": "system",
                "content": SUMMARY_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Hier ist eine Liste von JSON-Objekten. "
                            "Jedes Objekt repräsentiert eine zusammengefasste Vorlesungsfolie.\n\n"
                            f"{slides}"
                        )
                    }
                ]
            }
        ]
        # invoke the model with the message
        response = self.model.invoke(messages)
    
        # Save response to markdown file
        with open(RESOURCES_DIR + "/summary.md", "w", encoding="utf-8") as f:
            f.write(response.content)
    
    def summary_to_mind_map(self):
        """Creates mind map nodes and edges that are saved in a json file"""
        with open(RESOURCES_DIR + "/summary.md", "r") as f:
            md_summary = f.read()
        # combine a new prewritten prompt and the summary.md to a message list
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

        response = self.model.invoke(messages)

        with open(NODES_EDGES_PATH, "w", encoding="utf-8") as f:
            f.write(response.content)

    def _load_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="ignore")

    def _png_to_base64_url(self, png_path: Path) -> str:
        data = png_path.read_bytes()
        b64 = base64.b64encode(data).decode()
        return f"data:image/png;base64,{b64}"

    def run(self) -> None:
        self.single_slide_summary()
        self.summarize()
        self.summary_to_mind_map()

@dataclass
class ResponseFormat:
    """Response schema for the agent"""
    #quick and concise summary of the lecture enabling the reader to know what general topic the lecture is about if pdf available
    quick_concise_summary: str
    #summarized list of topics / important subtopics and how they are connected so that the user can create a mind map on the base of the response if pdf available
    summary_topics_connections: str