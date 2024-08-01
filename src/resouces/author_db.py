from .database import authors_db
from .entity_db import EntityDB
from .paper_db import PaperDB

class AuthorDB(EntityDB):
    """
    A class to manege actions onto the authors JSON objects
    """

    def __init__(self) -> None:
        super().__init__()
        self._set_database(authors_db)

    # Overriding
    def get_by_id(self, entity_id: int) -> dict:
        self.filter_by_number("Author_id", entity_id)

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
                case "Name":
                    self.filter_by_string(key, value)

    def get_papers(self, author_id: int) -> list[dict]:
        """
        Return the authors list of papers 
        """
        papers: list[dict] = []

        author: dict = self.get_by_id(author_id)
        if not author:
            return papers

        for paper_id in author["Papers"]:
            paper_database: PaperDB = PaperDB()
            paper: dict = paper_database.get_by_id(paper_id)

            if paper:
                papers.append(paper)
        return papers
