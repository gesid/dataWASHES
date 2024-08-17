from typing import Any
from .author_db import AuthorDB
from .paper_db import PaperDB


class StatisticsCalculator:

    @staticmethod
    def authors_rank(rank_size: int) -> list[dict[str, Any]]:
        author_db = AuthorDB()
        sorted_author_db = sorted(
            author_db.get_data()[0],
            reverse=True,
            key=lambda author: len(author["Papers"])
        )[:rank_size]
        return sorted_author_db

    @staticmethod
    def most_cited_papers(rank_size: int) -> list[dict[str, Any]]:
        papers_db = PaperDB()
        sorted_papers_db = sorted(
            papers_db.get_data()[0],
            reverse=True,
            key=lambda paper: len(paper["Cited_by"])
        )[:rank_size]
        return sorted_papers_db
