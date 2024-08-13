from .database import editions_db
from .entity_db import EntityDB
from .paper_db import PaperDB

class EditionDB(EntityDB):
    """
    A class to manege actions onto the editions JSON objects
    """

    def __init__(self) -> None:
        super().__init__()
        self._set_database(editions_db)

    # Overriding
    def get_by_id(self, entity_id: int) -> dict | None:
        self.filter_by_number("Edition_id", entity_id)
        if self.is_empty():
            return None
        return self._get_database()[0]

    # Overriding
    def filter_by(self, query_object: dict) -> None:
        if not isinstance(query_object, dict):
            raise ValueError()

        for key, value in query_object.items():
            if not value:
                continue

            match key:
                case "Year":
                    self.filter_by_number(key, value)

    def get_papers(self, edition_id: int) -> PaperDB | None:
        """
        Return the editions list of papers 
        """
        papers = PaperDB()
        edition = self.get_by_id(edition_id)
        if not edition:
            return None
        papers.filter_by_list_of_ids(edition["Papers"])
        return papers
