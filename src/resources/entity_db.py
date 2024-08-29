from abc import abstractmethod, ABCMeta
from collections.abc import Iterator
from api_utils import paginate


class EntityDB(metaclass=ABCMeta):
    """
    A class to manage actions onto the JSON objects
    """

    def __init__(self) -> None:
        self.__database: list[dict] = []

    @property
    def data(self) -> list[dict]:
        return self.__database

    @data.setter
    def data(self, value: list[dict]) -> None:
        pass

    def total_count(self) -> int:
        """
        Returns the number of objects in the database
        """
        return len(self.data)

    def is_empty(self) -> bool:
        """
        Returns ``True`` if the database is empty
        """
        return self.total_count() == 0

    def filter_by_string_key(self, key: str, value: str) -> None:
        """
        Filter the database considering a key value of type ``string``
        """
        self._set_database([
            entity for entity in self.data
            if value.lower() in entity[key].lower()
        ])

    def filter_by_string_list_key(self, key: str, value: str) -> None:
        """
        Filter the database considering a key value of type ``list of string``
        """
        self._set_database([
            entity for entity in self.data
            if any(value.lower() in item.lower() for item in entity[key])
        ])

    def filter_by_enum_key(self, key: str, value: str) -> None:
        """
        Filter the database considering a key value of type ``enum``
        """
        self._set_database([
            entity for entity in self.data
            if value.lower() == entity[key].lower()
        ])

    def filter_by_number_key(self, key: str, number: int) -> None:
        """
        Filter the database considering a key value of type ``int``
        """
        self._set_database([
            entity for entity in self.data
            if number == entity[key]
        ])

    def get_paginated_response(self) -> tuple[dict | None, int]:
        """
        Returns the data of the database paginated, also the response code\n
        
        :returns:
        (data, 404) - When the database is empty.
        (data, 200) - When the paginate process is successful.

        Raises:
            PaginateError: when the paginate process fails
        """
        if self.is_empty():
            return None, 404
        return paginate(self.data), 200

    def _set_database(self, new_database: list[dict]) -> None:
        """
        Changes the database object
        """
        self.__database = new_database

    @abstractmethod
    def get_by_id(self, entity_id: int) -> dict | None:
        """
        Returns the object identified by the ``id``
        """

    @abstractmethod
    def filter_by(self, query_object: dict[str, str]) -> None:
        """
        Filter the database
        """

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Iterator[dict]:
        return iter(self.data)

    def __bool__(self) -> bool:
        return bool(self.data)

    def __getitem__(self, item: int) -> dict:
        return self.data[int(item)]
