from abc import abstractmethod, ABCMeta

class EntityDB(metaclass=ABCMeta):
    """
    A class to manage actions onto the JSON objects
    """

    def __init__(self) -> None:
        self.__database: list[dict] = []

    def total_count(self) -> int:
        """
        Returns the number of objects in the database
        """
        return len(self._get_database())

    def is_empty(self) -> bool:
        """
        Returns ``True`` if the database is empty
        """
        return self.total_count() == 0

    def filter_by_string(self, key: str, value: str) -> None:
        """
        Filter the database considering a key of type ``string``
        """
        self._set_database([
            entity for entity in self._get_database()
            if value.lower() in entity[key].lower()
        ])

    def filter_by_vector_string(self, key: str, value: str) -> None:
        """
        Filter the database considering a key of type ``vector of string``
        """
        self._set_database([
            entity for entity in self._get_database()
            if any(value.lower() in item.lower() for item in entity[key])
        ])

    def filter_by_enum(self, key: str, value: str) -> None:
        """
        Filter the database considering a key of type ``enum``
        """
        self._set_database([
            entity for entity in self._get_database()
            if value.lower() == entity[key].lower()
        ])

    def filter_by_number(self, key: str, number: int) -> None:
        """
        Filter the database considering a key of type ``int``
        """
        self._set_database([
            entity for entity in self._get_database()
            if int(number) == entity[key]
        ])

    def get_data(self) -> tuple[dict[list], int]:
        """
        Returns the data of the database with the response code\n
        404 - When the database is empty\n
        200 - When the database is not empty
        """
        if self.is_empty():
            return self._get_database(), 404
        return self._get_database(), 200

    def _get_database(self) -> list[dict]:
        """
        Return the database object
        """
        return self.__database

    def _set_database(self, new_database: list[dict]) -> None:
        """
        Changes the database object
        """
        self.__database = new_database

    @abstractmethod
    def get_by_id(self, entity_id: int) -> dict:
        """
        Returns the object identified by the ``id``
        """

    @abstractmethod
    def filter_by(self, query_object: dict) -> list[dict]:
        """
        Filter the database
        """
