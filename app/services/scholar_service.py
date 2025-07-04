import arxiv
from typing import List, Dict
from datetime import datetime, timedelta

class ScholarService:
    def __init__(self):
        self.client = arxiv.Client()

    def search_new_papers(self, keyword: str) -> List[Dict]:
        """
        Searches for new papers on arXiv based on the given keyword.
        Returns a list of dictionaries, each representing a paper.
        """
        search_query = f'ti:"{keyword}" OR abs:"{keyword}"'
        # Search for papers published in the last 7 days
        # This is a placeholder; a more robust solution would track the last search time.
        # seven_days_ago = datetime.now() - timedelta(days=7)
        # query = f'{search_query} AND submittedDate:[{seven_days_ago.strftime("%Y%m%d%H%M%S")} TO {datetime.now().strftime("%Y%m%d%H%M%S")}]'

        search = arxiv.Search(
            query=search_query,
            max_results=10,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )

        papers_data = []
        for result in self.client.results(search):
            papers_data.append({
                "title": result.title,
                "url": result.pdf_url,
                "summary": result.summary,
                "authors": [author.name for author in result.authors],
                "published_date": result.published,
                "arxiv_id": result.entry_id.split('/')[-1]
            })
        return papers_data