from .dataset import editions_db
from .entity_db import EntityDB
from .paper_db import PaperDB


class EditionDB(EntityDB):
    """
    A class to manage actions onto the edition's JSON dataset.\n
    Each instance of EditionDB starts with a reference to the edition's dataset.\n
    When any filter action is executed, another reference is created, leaving the actual dataset unchanged.\n
    That means the object is supposed to be used for only one action.\n
    If you need to perform more than one filter action, you are going to need to create another instance.\n
    """

    def __init__(self) -> None:
        super().__init__()
        self._set_database(editions_db)

    # Overriding
    def get_by_id(self, entity_id: int) -> dict | None:
        self.filter_by_number_key("Edition_id", entity_id)
        if self.is_empty():
            return None
        return self[0]

    # Overriding
    def filter_by(self, query_object: dict[str, str]) -> None:
        if not isinstance(query_object, dict):
            raise ValueError()
        for key, value in query_object.items():
            if not value:
                continue
            match key:
                case "Year":
                    if not value.isnumeric():
                        raise ValueError("Invalid Year, must be numeric")
                    self.filter_by_number_key(key, int(value))

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
