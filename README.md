# PDF2Mindmap

## Overview
**PDF2Mindmap** is a CLI-based tool that automatically transforms **academic lecture PDFs** into  
**exam-oriented summaries** and **high-level mindmaps**.

The project is specifically designed for **university lectures** and focuses on:
- understanding slide-based PDFs,
- creating consolidated lecture summaries,
- and generating structured mindmaps for learning and revision.

The workflow combines **PDF parsing**, **multimodal LLM prompts**, and **structured post-processing**
to turn unstructured lecture material into usable study artifacts.

---

## Features
- Extract **Markdown text** and **page images** from lecture PDFs
- Create **slide-level structured summaries** (JSON)
- Aggregate all slides into a **1–3 page exam-ready Markdown summary**
- Generate **high-level mindmaps** with:
  - a central root topic (lecture title)
  - main branches based on lecture structure
- Designed for **academic / exam preparation**, not generic PDFs

---

## Installation

#### Prerequisites
- Python 3.12 or higher
- An OpenAI-compatible API key (set via environment variable)
- The following libraries (installed automatically):
  - `langchain`
  - `langchain-openai`
  - `graphviz`
  - `pymupdf`
  - `pymupdf4llm`
  - `python-dotenv`

1. Clone the repository:

    ```bash
    git clone https://github.com/domynyk99/PDF2Mindmap.git
    cd PDF2Mindmap
    ```

2. Install the package (or dependencies):

    ```bash
    pip install .
    ```

3. Set your API key

    Create a `.env` file (or rename `.env.example` to `.env`) and add your API key:

    ```env
    OPENAI_API_KEY="YOUR_API_KEY_HERE"
    ```

---

## Usage

1. Place your lecture PDF in the `resources/` directory and rename it to `lecture.pdf`.

2. Run the summarization pipeline from the project root:

   ```bash
   summarize
   ```

3. The program will execute the following steps automatically:

    - Convert the PDF into one Markdown file and one image per slide/page
    - Store the extracted files in:
        - `resources/mds/`
        - `resources/images/`
    - Generate slide-level summaries using an AI agent
    - Aggregate all slide summaries into a single exam-oriented `summary.md`
    - Create nodes and edges representing the lecture’s conceptual structure
    - Build a high-level mindmap based on this structure

4. All generated outputs are saved inside the `resources/` directory:

    - `summary.md` – final lecture summary
    - `nodes_edges.json` – structured mindmap data
    - `mindmap/` – rendered mindmap files

---

## Why I built this

I built this project to deepen my understanding of **LangChain fundamentals** and to explore how
**AI agent workflows** can be designed and orchestrated in practice.

In the process, I learned how to:
- extract and structure content from **lecture PDFs** using Python,
- combine **textual and visual information** (Markdown + images) for more robust document understanding,
- design **multi-step LLM pipelines** for summarization and abstraction,
- and generate **mindmaps** by transforming structured nodes and edges into visual representations.

The project helped me bridge the gap between raw, unstructured study material and
well-organized learning artifacts such as summaries and mindmaps, while gaining hands-on experience
with modern AI tooling and document-processing workflows.

---

## Future Improvements

- Replace the current static Graphviz-based output with an **interactive GUI** that allows users to
  create, edit, and delete nodes after the AI has generated the initial mindmap structure.
  This would enable manual refinement, better personalization, and a more visually appealing result.

- Improve the PDF processing pipeline by **grouping slides into semantic subtopics** before
  summarization. Instead of processing every slide individually, the system could work on
  larger, conceptually connected sections of a lecture.

  This approach would:
  - provide the AI with more meaningful context,
  - reduce the number of input and output tokens,
  - improve overall reasoning quality,
  - and make the pipeline faster and more cost-efficient.
