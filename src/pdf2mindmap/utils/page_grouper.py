# Standard library imports
import os

# Third-party imports
import hdbscan
from sentence_transformers import SentenceTransformer

# Local application imports
from src.pdf2mindmap.utils.constants import RESOURCES_DIR

class PageGrouper():
    def __init__(self):
        self.md_dir_path = RESOURCES_DIR / "markdowns"
        self.texts = None
        self.contextualized_text = None
        self.embeddings = None
        self.groups = None
        
    def run(self):
        self.texts = self.dict_to_texts(self.page_line_to_dict(lines_to_consider=3))
        self.contextualized_text = self.contextualize_pages(self.texts)
        
        self.embeddings = self.generate_embeddings(self.contextualized_text)
        self.cluster_list = self.cluster_embeddings(self.embeddings)
        # print("Cluster List:")
        # print(self.cluster_list)

        self.groups = self.chunk_to_dict(self.cluster_list)
        # print("Pairs: ")
        # print(pairs)
    
    def page_line_to_dict(self, lines_to_consider: int) -> dict:
        """
        Extract the first lines of each markdown file and map them to their page number.

        This function iterates over all files in 'markdown_directory_path', reads the
        first 'lines_to_consider' lines from each file, and stores them in a dictionary
        keyed by page number.

        The page number is extracted from the filename using 'file_name[5:7]' and is
        returned as a string.

        :param lines_to_consider: Number of lines to read from the beginning of each file.
        :type lines_to_consider: int
        
        :return: Mapping from page number (string) to the concatenated first lines of that page.
        :rtype: dict[str, str]
        
        :raises ValueError: If 'lines_to_consider' is less than 1.
        """
        page_line_pairs = {}

        for file_name in os.listdir(self.md_dir_path):
            file_path = os.path.join(self.md_dir_path, file_name)
            page_number = file_name[5:7]
            first_lines = ""
            with open(file_path, "r", encoding="utf-8") as f:
                for _ in range(lines_to_consider):
                    try:
                        first_lines += next(f)
                    except StopIteration:
                        break
            page_line_pairs.update({page_number: first_lines})
        
        return page_line_pairs

    def dict_to_texts(self, slides: dict) -> list[str]:
        """
        Convert a page-indexed mapping into a list of page texts sorted by page number.
        
        :param slides: Mapping from page number to page text. Keys must be convertible to int.
        :type slides: dict
        
        :return: Page texts ordered by ascending page number.
        :rtype: list[str]
        """""
        pages = sorted(slides.keys(), key=int)
        texts = []
        for p in pages:
            t = slides[p]
            texts.append(t)

        return texts

    def contextualize_pages(self, texts: list[str], window: int=1) -> list[str]:
        """
        Build contextualized page strings by concatenating neighboring pages.

        For each page ``i`` this returns a context string consisting of:
        - the previous page (``i - window``), if it exists
        - the current page twice (center-boosted)
        - the next page (``i + window``), if it exists

        The parts are joined with newlines.
        
        :param texts: Page texts in page order (text[0] corresponds to the text on page 1).
        :type texts: list[str]
        
        :param window: Neighbor distance to include (must be >= 0). For example, window=1
                   includes immediate neighbors.
        :type window: int

        :return: List of contextualized texts with the same length as input-parameter 'texts'.
        :rtype: list[str]
        """
        out=[]
        n=len(texts)
        for i in range(n):
            parts=[]
            if i-window >= 0:
                parts.append(texts[i-window])
            parts.append(texts[i] + "\n" + texts[i])   # center boosted
            if i+window < n:
                parts.append(texts[i+window])
            out.append("\n".join(parts))
        return out

    def generate_embeddings(self, texts: list[str]):
        """
        Generate sentence embeddings for each input text using SentenceTransformer.
        
        :param texts: List of (optionally contextualized) page texts.
        :type texts: list[str]

        :return: Embeddings of these pages/strings
        """
        model = SentenceTransformer("sentence-transformers/distiluse-base-multilingual-cased-v1")

        embeddings = model.encode(texts, normalize_embeddings=True)

        return embeddings

    def cluster_embeddings(self, embeddings) -> list[int]:
        """
        Cluster embedding vectors with HDBSCAN.

        Uses HDBSCAN with 'min_samples=2' and 'min_cluster_size=2' to assign each
        embedding to a cluster. Noise points are labeled '-1' by HDBSCAN 

        :param embeddings: Embeddings generated by the SentenceTransformer model in self.generate_embeddings(self, texts: list)

        :return: Cluster labels for each page/text.
                For example: list[0] = 1 means page_01 of the lecture belongs to cluster 1
        :rtype: list[int]
        """
        hdb = hdbscan.HDBSCAN(min_samples=2, min_cluster_size=2).fit_predict(embeddings)
        cluster_list = hdb.tolist()
        
        return cluster_list
        
    def chunk_to_dict(self, cluster_list: list[int]) -> dict:
        """
        Group consecutive pages that share the same cluster label.

        Pages are grouped only when the same cluster label appears in consecutive
        positions. If the same cluster label appears again later, it will form a new group.

        Example:
            ``[1, 1, 2, 2, 1]`` -> {0: [1, 2], 1: [3, 4], 2: [5]}
               
        :param cluster_list: Cluster label per page (index 0 corresponds to page 1).
        :type cluster_list: list[int]
        
        :return: Dictionary of group:Mapping from group index to 1-based page numbers.
        :rtype: dict[int, list[int]]
        """
        pairs = {}
        group = 0
        for page_num in range(len(cluster_list)):
            if page_num == 0:
                pairs.update({group: [page_num+1]})
                continue

            if cluster_list[page_num] == cluster_list[page_num-1]:
                pairs[group].append(page_num+1)
            else:
                group += 1
                pairs.update({group: [page_num+1]})
        return pairs
    


 
if __name__ == "__main__":
    page_grouper = PageGrouper()
    page_grouper.run()