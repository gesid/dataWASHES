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
    def get_by_id(self, id: int) -> dict:
        self.filter_by_number(id, "Paper_id")

        if self.is_empty():
            return {}
        return self._get_database()[0]

    # Overriding
    def filter_by(self, keys: dict) -> list[dict]:
        if not isinstance(keys, dict):
            raise ValueError()

        for key, value in keys.items():
            if key in self._get_database():
                match key:
                    case "Year":
                        self.filter_by_number(key, value)
                    case "Type":
                        if any(value == paper_type for paper_type in PaperTypes):
                            self.filter_by_enum(key, value)
                        else:
                            raise ValueError()
    