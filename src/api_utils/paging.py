from math import ceil
from flask_restx import Namespace # type: ignore
from flask import request
from .abort_func import abort_execution
from .constants import PAGE_PARAM, PER_PAGE_PARAM

def paginate(ns: Namespace, data: list[dict], default_page: int = 1, default_per_page: int = 10) -> dict | None:
    """
    Paginate the given data.

    :param data: The list of items to paginate
    :param default_page: The default page number if not provided
    :param default_per_page: The default number of items per page if not provided
    :return: A dictionary with paginated data, paging infos and links to other pages
    """
    try:
        page = int(request.args.get(PAGE_PARAM, default_page))
        per_page = int(request.args.get(PER_PAGE_PARAM, default_per_page))

        if page < 1 or per_page < 1:
            abort_execution(ns, "Page and per_page must be positive integers", 400)

        total_count: int = len(data)
        page_count: int = ceil(total_count / per_page)
        start: int = (page - 1) * per_page
        end: int = start + per_page

        if start >= total_count:
            abort_execution(ns, "Page number out of range", 400)

        paginated_data: list[dict] = data[start:end]

        return {
            "data": paginated_data,
            "paging": {
                "page": page,
                "per_page": per_page,
                "page_count": page_count,
                "total_count": total_count,
            },
            "links": {
                "self": f"{request.path}?page={page}&per_page={per_page}",
                "first": f"{request.path}?page={1}&per_page={per_page}",
                "previous": f"{request.path}?page={page - 1}&per_page={per_page}" if page > 1 else "",
                "next": f"{request.path}?page={page + 1}&per_page={per_page}" if page < page_count else "",
                "last": f"{request.path}?page={page_count}&per_page={per_page}",
            }
        }
    except ValueError:
        abort_execution(ns, "Page and per_page must be positive integers", 400)
        return None
