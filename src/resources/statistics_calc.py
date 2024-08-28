from typing import Any
from api_utils import memoize
from .author_db import AuthorDB
from .paper_db import PaperDB


class StatisticsCalculator:

    @staticmethod
    @memoize
    def authors_rank() -> list[dict[str, Any]]:
        author_db = AuthorDB()
        sorted_author_db = sorted(
            author_db.get_data()[0],
            reverse=True,
            key=lambda author: len(author["Papers"])
        )
        return sorted_author_db

    @staticmethod
    @memoize
    def most_cited_papers() -> list[dict[str, Any]]:
        papers_db = PaperDB()
        sorted_papers_db = sorted(
            papers_db.get_data()[0],
            reverse=True,
            key=lambda paper: len(paper["Cited_by"])
        )
        return sorted_papers_db

    @staticmethod
    @memoize
    def institution_rank() -> list[dict[str, int]]:
        papers_db = PaperDB()
        institutions: dict[str, int] = {}
        for paper in papers_db.get_data()[0]:
            institution = paper["Authors"][0]["Institution_acronym"]
            if institution not in institutions:
                institutions[institution] = 1
            else:
                institutions[institution] += 1
        institutions_rank = sorted(
            institutions.items(),
            reverse=True,
            key=lambda x: x[1]
        )
        return [
            {"institution": institution, "publications": publications}
            for institution, publications in institutions_rank
        ]

    @staticmethod
    @memoize
    def states_rank() -> list[dict[str, int]]:
        papers_db = PaperDB()
        states: dict[str, int] = {}
        for paper in papers_db.get_data()[0]:
            state = paper["Authors"][0]["State"]
            if state not in states:
                states[state] = 1
            else:
                states[state] += 1
        institutions_rank = sorted(
            states.items(),
            reverse=True,
            key=lambda x: x[1]
        )
        return [
            {"state": state, "publications": publications}
            for state, publications in institutions_rank
        ]

    @staticmethod
    @memoize
    def keywords_cloud() -> list[dict]:
        key_words: dict[str, int] = {}
        paper_db = PaperDB().get_data()[0]
        for paper in paper_db:
            keys = paper["Keywords"].split(', ')
            for key in keys:
                if key.lower() in key_words:
                    key_words[key.lower()] += 1
                elif key != '#':
                    key_words[key.lower()] = 1
        sorted_key_words = sorted(
            key_words.items(),
            reverse=True,
            key=lambda x: x[1]
        )
        return [
            {"keyword": key, "count": count}
            for key, count in sorted_key_words
        ]

    @staticmethod
    @memoize
    def test() -> int:
        i = 0
        for _ in range(1_000_000_00):
            i += 1
        return i