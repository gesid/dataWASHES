from .database import authors_db
from .entity_db import EntityDB

class AuthorDB(EntityDB):

    def __init__(self) -> None:
        super().__init__()
        self._set_database(authors_db)

    # Overriding
    def get_by_id(self, entity_id: int) -> dict:
        """
        Returns the object identified by the ``id``
        """
        self.filter_by_number("Author_id", entity_id)

        if self.is_empty():
            return {}
        return self.get_data()[0]

    # Overriding
    def filter_by(self, query_object: dict) -> list[dict]:
        """
        Filter the database
        """
