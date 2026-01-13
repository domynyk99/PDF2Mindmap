# PDF2Mindmap

## Overview
**PDF2Mindmap** is a CLI-based tool that automatically transforms **academic lecture PDFs** into  
**exam-oriented summaries** and **high-level mindmaps**.

The project is specifically designed for **university lecture slides** and focuses on:
- understanding slide-based PDFs,
- grouping semantically related slides,
- creating consolidated lecture summaries,
- and generating structured mind maps for learning and revision.

The workflow combines **PDF parsing**, **semantic clustering**, **multimodal LLM prompts**,
and **structured post-processing** to turn unstructured lecture material into usable study artifacts.

> **Note:** The current pipeline is primarily optimized for **German lecture slides** and
> therefore produces **German summaries and mind maps**. Support for additional languages
> (including English) is planned for a future update.
---

## Features
- Extract **Markdown text** and **page images** from lecture PDFs
- **Semantically group related slides** using embedding-based clustering
- Create **group-level structured summaries** (JSON)
- Aggregate all slide groups into a **1–3 page exam-ready Markdown summary**
- Generate **high-level mind maps** with:
  - a central root topic (lecture title)
  - main branches based on lecture structure
- Designed specifically for **academic / exam preparation**, not generic PDFs

---

## Installation

#### Prerequisites
- Python 3.12 or higher
- An OpenAI-compatible API key (set via environment variable)

##### Python Dependencies
The following libraries are installed automatically:
- `langchain`
- `langchain-openai`
- `pymupdf`
- `pymupdf-layout`
- `pymupdf4llm`
- `python-dotenv`
- `yfiles_graphs_for_streamlit`
- `hdbscan`
- `sentence-transformers`

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
    - Generate embeddings for all slides and cluster semantically related slides
    - Create group-level summaries using multimodal LLM prompts (text + images)
    - Aggregate all group summaries into a single exam-oriented `summary.md`
    - Create nodes and edges representing the lecture’s conceptual structure
    - Build a high-level mindmap based on this structure

4. All generated outputs are saved inside the `resources/` directory:

    - `summary.md` – final lecture summary
    - `nodes_edges.json` – structured mindmap data

5. To visualize the mind map using the Streamlit app, run:

  ```bash
  streamlit run src/pdf2mindmap/main/streamlit_mindmap.py
  ```

---

## Why I built this

I built this project to deepen my understanding of **LangChain fundamentals** and to explore how
**AI agent workflows** can be designed and orchestrated in practice.

In the process, I learned how to:
- extract and structure content from **lecture PDFs** using Python,
- apply semantic embeddings and clustering to group related content,
- combine **textual and visual information** (Markdown + images) for more robust document understanding,
- design **multi-step LLM pipelines** for summarization and abstraction,
- and generate **mindmaps** by transforming structured nodes and edges into visual representations.

The project helped me bridge the gap between raw, unstructured study material and
well-organized learning artifacts such as summaries and mindmaps, while gaining hands-on experience
with modern AI tooling and document-processing workflows.

---

## Future Improvements

- Possibly create a GUI where the user can simply drop in a PDF, start the pipeline with a button,
and see progress indicators (e.g. a progress bar) for a more pleasant user experience.
- Extend language support beyond German and allow summaries and mind maps to be generated
  in other languages (e.g. English).
