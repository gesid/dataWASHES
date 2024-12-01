from api_utils import memoize
from . import EditionDB
from .author_db import AuthorDB
from .paper_db import PaperDB
from .award_papers_db import AwardPapersDB


class StatisticsCalc:

    def __init__(self):
        self.__award_papers = AwardPapersDB()

    @property
    def award_winning_papers(self) -> list[dict]:
        return self.__award_papers.data

    @staticmethod
    @memoize
    def authors_rank() -> list[dict[str, ...]]:
        author_db = AuthorDB()
        sorted_author_db = sorted(
            author_db.data,
            reverse=True,
            key=lambda author: len(author["Papers"])
        )
        return sorted_author_db

    @staticmethod
    @memoize
    def most_cited_papers() -> list[dict[str, ...]]:
        papers_db = PaperDB()
        sorted_papers_db = sorted(
            papers_db.data,
            reverse=True,
            key=lambda paper: len(paper["Cited_by"])
        )
        return sorted_papers_db

    @staticmethod
    @memoize
    def institution_rank() -> list[dict[str, str | int]]:
        papers_db: PaperDB = PaperDB()
        institutions: dict[str, int] = {}
        for paper in papers_db:
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
    def states_rank() -> list[dict[str, str | int]]:
        papers_db: PaperDB = PaperDB()
        states: dict[str, int] = {}
        for paper in papers_db:
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
    def publications_by_years() -> list[dict[str, int]]:
        editions_db: EditionDB = EditionDB()
        publications_by_year: list[dict[str, int]] = []
        for edition in editions_db:
            year = edition["Year"]
            publications = len(edition["Papers"])
            publications_by_year.append({"year": year, "publications": publications})
        return publications_by_year

    @staticmethod
    @memoize
    def keywords_cloud() -> list[dict]:
        key_words: dict[str, int] = {}
        paper_db = PaperDB()
        for paper in paper_db:
            keys = paper["Keywords"].split(', ')
            for word in keys:
                for key in word.split():
                    if key == 'de' or key == 'e':
                        continue
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
    def papers_by_languages() -> list[dict[str, str | int]]:
        paper_db: PaperDB = PaperDB()
        languages: dict[str, int] = {}
        for paper in paper_db:
            if paper["Language"] not in languages:
                languages[paper["Language"]] = 1
            else:
                languages[paper["Language"]] += 1
        sorted_languages = sorted(
            languages.items(),
            reverse=True,
            key=lambda x: x[1]
        )
        return [
            {"language": language, "publications": count}
            for language, count in sorted_languages
        ]

    @staticmethod
    @memoize
    def publications_by_years_by_languages() -> dict:
        editions_db: EditionDB = EditionDB()
        languages = set()
        publications_by_lang: list[dict] = []
        for edition in editions_db:
            key = edition["Year"]
            publications_by_lang.append({'year': key})
            papers_db: PaperDB = PaperDB()
            papers_db.filter_by_list_of_ids(edition["Papers"])
            for paper in papers_db:
                if paper["Language"] not in publications_by_lang[-1]:
                    publications_by_lang[-1][paper["Language"]] = 1
                    languages.add(paper["Language"])
                else:
                    publications_by_lang[-1][paper["Language"]] += 1
        return {
            'data': publications_by_lang,
            'langs': list(languages),
        }
