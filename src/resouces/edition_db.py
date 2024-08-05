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
    def get_by_id(self, entity_id: int) -> dict:
        self.filter_by_number("Edition_id", entity_id)

        if self.is_empty():
            return {}
        return self.get_data()[0]

    # Overriding
    def filter_by(self, query_object: dict) -> list[dict]:
        if not isinstance(query_object, dict):
            raise ValueError()

        for key, value in query_object.items():
            if not value:
                continue

            match key:
                case "Year":
                    self.filter_by_number(key, value)

    def get_papers(self, edition_id: int) -> list[dict]:
        """
        Return the editions list of papers 
        """
        papers: list[dict] = []

        edition: dict = self.get_by_id(edition_id)
        if not edition:
            return papers

        for paper_id in edition["Papers"]:
            paper_database: PaperDB = PaperDB()
            paper: dict = paper_database.get_by_id(paper_id)

            if paper:
                papers.append(paper)
        return papers
