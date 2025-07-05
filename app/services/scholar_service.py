import arxiv
from typing import List, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ScholarService:
    def __init__(self):
        self.client = arxiv.Client()

    def search_new_papers(self, keyword: str) -> List[Dict]:
        """
        Searches for new papers on arXiv based on the given keyword.
        Returns a list of dictionaries, each representing a paper.
        """
        search_query = f'ti:"{keyword}" OR abs:"{keyword}"'

        search = arxiv.Search(
            query=search_query,
            max_results=10,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )

        papers_data = []
        try:
            for result in self.client.results(search):
                papers_data.append({
                    "title": result.title,
                    "url": result.pdf_url,
                    "summary": result.summary,
                    "authors": [author.name for author in result.authors],
                    "published_date": result.published,
                    "arxiv_id": result.entry_id.split('/')[-1]
                })
        except Exception as e:
            logger.error(f"Error searching arXiv for keyword '{keyword}': {e}")
            # Depending on the desired fault tolerance, you might want to re-raise,
            # return an empty list, or implement a retry mechanism here.
        return papers_data