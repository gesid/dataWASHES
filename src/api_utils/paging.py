from math import ceil
from urllib.parse import urlencode

from flask import request

from .constants import PAGE_PARAM, PER_PAGE_PARAM


class PaginateError(Exception):
    pass


def paginate(data: list[dict], default_page: int = 1, default_per_page: int = 10) -> dict:
    """
    Paginate the given data.

    :param data: The list of items to paginate
    :param default_page: The default page number if not provided
    :param default_per_page: The default number of items per page if not provided
    :return: A dictionary with paginated data, paging infos and links to other pages

    Raises:
        PaginateError: When the paginate process fails
    """
    try:
        page = int(request.args.get(PAGE_PARAM, default_page))
        per_page = int(request.args.get(PER_PAGE_PARAM, default_per_page))
    except (TypeError, ValueError):
        raise PaginateError("Page and per_page must be positive integers") from None

    if page < 1 or per_page < 1:
        raise PaginateError("Page and per_page must be positive integers")

    total_count: int = len(data)
    page_count: int = ceil(total_count / per_page)
    start: int = (page - 1) * per_page
    end: int = start + per_page

    if start >= total_count:
        raise PaginateError("Page number out of range")

    paginated_data: list[dict] = data[start:end]

    def build_link(page_number: int) -> str:
        """
        Build a pagination link preserving every query parameter except the
        paging ones (which are recomputed from ``page_number``).
        """
        query_params = [(PAGE_PARAM, str(page_number)), (PER_PAGE_PARAM, str(per_page))]
        query_params.extend(
            (key, value)
            for key, value in request.args.items()
            if key not in (PAGE_PARAM, PER_PAGE_PARAM)
        )
        return f"{request.path}?{urlencode(query_params)}"

    return {
        "data": paginated_data,
        "paging": {
            "page": page,
            "per_page": per_page,
            "page_count": page_count,
            "total_count": total_count,
        },
        "links": {
            "self": build_link(page),
            "first": build_link(1),
            "previous": build_link(page - 1) if page > 1 else "",
            "next": build_link(page + 1) if page < page_count else "",
            "last": build_link(page_count),
        },
    }
