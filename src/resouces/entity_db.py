from abc import abstractmethod, ABCMeta

class EntityDB(metaclass=ABCMeta):
    """
    A class to manege actions onto the JSON objects
    """

    def total_count(self) -> int:
        """
        Returns the number os objects in the database
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
        Filter the database considering a key of type vector of string
        """
        self._set_database([
            entity for entity in self._get_database()
            if any(value.lower() in item.lower() for item in entity[key])
        ])

    def filter_by_enum(self, key: str, value: str) -> None:
        """
        Filter the database considering a key of type ``Enum``
        """
        self._set_database([
            entity for entity in self._get_database()
            if value.lower() == entity[key].lower()
        ])

    def filter_by_number(self, key: str, number: int | float) -> None:
        """
        Filter the database considering a key of type ``int`` or ``float``
        """
        self._set_database([
            entity for entity in self._get_database()
            if number == entity[key]
        ])

    @abstractmethod
    def _get_database(self) -> list[dict]:
        """
        Return the database object
        """

    @abstractmethod
    def _set_database(self, new_database) -> None:
        """
        Changes the database object
        """

    @abstractmethod
    def get_by_id(self, paper_id: int) -> dict:
        """
        Returns the object identified by the ``id``
        """

    @abstractmethod
    def filter_by(self, query_object: dict) -> list[dict]:
        """
        Filter the database
        """
    def get_data(self) -> dict[list]:
        return self._get_database()
