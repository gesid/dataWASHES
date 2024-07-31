from enum import Enum
from .database import papers_db
from .entity_db import EntityDB

class PaperTypes(Enum):
    """
    The types of papers
    """
    SHORT_PAPER = "Short paper"
    POSTER = "Poster"
    FULL_PAPER = "Full paper"

class PaperDB(EntityDB):
    """
    A class to manege actions onto the papers JSON objects
    """
    def __init__(self) -> None:
        self.__database = papers_db

    # Overriding
    def _get_database(self) -> list[dict]:
        return self.__database

    # Overriding
    def _set_database(self, new_database) -> None:
        self.__database = new_database

    # Overriding
    def get_by_id(self, paper_id: int) -> dict:
        self.filter_by_number(paper_id, "Paper_id")

        if self.is_empty():
            return {}
        return self._get_database()[0]

    # Overriding
    def filter_by(self, query_object: dict) -> list[dict]:
        if not isinstance(query_object, dict):
            raise ValueError()

        for key, value in query_object.items():
            if not value: continue

            match key:
                case "Year":
                    self.filter_by_number(key, value)
                case "Type":
                    if any(value == paper_type.value for paper_type in PaperTypes):
                        self.filter_by_enum(key, value)
                    else:
                        raise ValueError("Invalid paper type")
                case "Title" | "Abstract" | "Resumo" | "Keywords" | "Download_link":
                    self.filter_by_string(key, value)
                case "Search":
                    self.filter_by_two_strings("Title", "Abstract", value)
                case "Author":
                    self.filter_by_author_string("Name", value)
                case "Institution" | "State":
                    self.filter_by_author_string(key, value)
                case "References" | "Cited_by":
                    self.filter_by_vector_string(key, value)

    def filter_by_two_strings(self, key1: str, key2: str, value: str) -> None:
        """
        Filter considering two keys of type ``string``
        """
        self._set_database([
                paper for paper in self._get_database()
                if value.lower() in paper[key1].lower() or
                value.lower() in paper[key2].lower()
        ])

    def filter_by_author_string(self, key: str, value: str) -> list[dict]:
        """
        Filter the database considering an author property
        """
        self._set_database([
            paper for paper in self._get_database()
            if any(value.lower() in author[key].lower() for author in paper["Authors"])
        ])
