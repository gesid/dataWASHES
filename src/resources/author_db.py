from .database import authors_db
from .entity_db import EntityDB
from .paper_db import PaperDB


class AuthorDB(EntityDB):
    """
    A class to manage actions onto the author's JSON dataset.\n
    Each instance of AuthorDB starts with a reference to the author's dataset.\n
    When any filter action is executed, another reference is created, leaving the actual dataset unchanged.\n
    That means the object is supposed to be used for only one action.\n
    If you need to perform more than one filter action, you are going to need to create another instance.\n
    """

    def __init__(self) -> None:
        super().__init__()
        self._set_database(authors_db)

    # Overriding
    def get_by_id(self, entity_id: int) -> dict | None:
        self.filter_by_number_key("Author_id", entity_id)
        if self.is_empty():
            return None
        return self[0]

    # Overriding
    def filter_by(self, query_object: dict[str, str]) -> None:
        if not isinstance(query_object, dict):
            raise ValueError("query_object must be a dictionary")
        for key, value in query_object.items():
            if not value:
                continue
            match key:
                case "Name":
                    self.filter_by_string_key(key, value)

    def get_papers(self, author_id: int) -> list[dict] | None:
        """
        Return the authors list of papers 
        """
        papers: list[dict] = []
        author = self.get_by_id(author_id)
        if not author:
            return None
        for paper_id in author["Papers"]:
            paper_database: PaperDB = PaperDB()
            paper = paper_database.get_by_id(paper_id)
            if paper:
                papers.append(paper)
        return papers
