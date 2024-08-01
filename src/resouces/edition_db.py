from .database import editions_db
from .entity_db import EntityDB

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
