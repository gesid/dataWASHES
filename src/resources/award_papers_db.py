from abc import ABC

from .dataset import award_papers_db
from .entity_db import EntityDB


class AwardPapersDB(EntityDB):
    """
    A class to manage actions onto the edition's JSON dataset.\n
    Each instance of AwardPapersDB starts with a reference to the award-winning paper's dataset.\n
    When any filter action is executed, another reference is created, leaving the actual dataset unchanged.\n
    That means the object is supposed to be used for only one action.\n
    If you need to perform more than one filter action, you are going to need to create another instance.\n
    """

    def __init__(self) -> None:
        super().__init__()
        self._set_database(award_papers_db)

    def filter_by(self, query_object: dict[str, str]) -> None:
        pass

    def get_by_id(self, entity_id: int) -> dict | None:
        pass

