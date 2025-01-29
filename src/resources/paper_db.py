from enum import Enum
from .dataset import papers_db
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
    A class to manage actions onto the paper's JSON dataset.\n
    Each instance of PaperDB starts with a reference to the paper's dataset.\n
    When any filter action is executed, another reference is created, leaving the actual dataset unchanged.\n
    That means the object is supposed to be used for only one action.\n
    If you need to perform more than one filter action, you are going to need to create another instance.\n
    """

    def __init__(self) -> None:
        super().__init__()
        self._set_database(papers_db)

    # Overriding
    def get_by_id(self, entity_id: int) -> dict | None:
        self.filter_by_number_key("Paper_id", entity_id)
        if self.is_empty():
            return None
        return self[0]

    # Overriding
    def filter_by(self, query_object: dict[str, str]) -> None:
        """
            Filter the database based on the provided 'query object'
            :param query_object: The dictionary containing the paper's keys and values to make the filtering
            :return: None
            :raises ValueError:

        """
        if not isinstance(query_object, dict):
            raise ValueError("query_object must be a dictionary")
        for key, value in query_object.items():
            if value:
                match key:
                    case "Paper_id" | "Year":
                        if not value.isnumeric():
                            raise ValueError(f"Invalid {value}, must be numeric")
                        self.filter_by_number_key(key, int(value))
                    case "Type":
                        if not self.is_valid_paper_type(value):
                            raise ValueError("Invalid paper type")
                        self.filter_by_enum_key(key, value)
                    case "Title" | "Abstract" | "Resumo" | "Keywords" | "Download_link":
                        self.filter_by_string_key(key, value)
                    case "Search":
                        self.filter_by_two_strings_keys("Title", "Abstract", value)
                    case "Author":
                        self.filter_by_author_string_key("Name", value)
                    case "Institution" | "State":
                        self.filter_by_author_string_key(key, value)
                    case "References" | "Cited_by":
                        self.filter_by_string_list_key(key, value)

    @staticmethod
    def is_valid_paper_type(value: str) -> bool:
        """
        Returns ``True`` if 'value' is a valid paper type ``False`` otherwise
        """
        if any(value.lower() == paper_type.value.lower() for paper_type in PaperTypes):
            return True
        return False

    def filter_by_two_strings_keys(self, key1: str, key2: str, value: str) -> None:
        """
        Filter considering two keys of type ``string``
        """
        self._set_database([
            paper for paper in self
            if value.lower() in paper[key1].lower() or value.lower() in paper[key2].lower()
        ])

    def filter_by_author_string_key(self, key: str, value: str) -> None:
        """
        Filter the database considering an author property
        """
        self._set_database([
            paper for paper in self
            if any(value.lower() in author[key].lower() for author in paper["Authors"])
        ])

    def get_abstracts(self) -> list[dict]:
        """
        Returns the abstract of all papers
        """
        return [
            {"Paper_id": paper["Paper_id"], "Abstract": paper["Abstract"]}
            for paper in self
        ]

    def filter_by_list_of_ids(self, papers_ids: list[int]) -> None:
        """
        filter the database considering a list of IDs
        """
        papers_ids_set: set = set(papers_ids)
        papers: list[dict] = []
        for paper in self:
            if paper["Paper_id"] in papers_ids_set:
                papers.append(paper)
        self._set_database(papers)

    def get_citations_by_id(self, paper_id: int) -> dict | None:
        """
        Returns the citations of the paper identified by the ``paper_id``
        """
        paper = self.get_by_id(paper_id)
        if not paper:
            return None
        return {
            "Paper_id": paper_id,
            "Cited_by": paper["Cited_by"]
        }

    def get_references_by_id(self, paper_id: int) -> dict | None:
        """
        Returns the references of the paper identified by the ``paper_id``
        """
        paper = self.get_by_id(paper_id)
        if not paper:
            return None
        return {
            "Paper_id": paper_id,
            "References": paper["References"]
        }
