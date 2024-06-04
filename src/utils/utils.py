from flask import request

def paginate(data, page_param='page', per_page_param='per_page', default_page=1, default_per_page=10):
    """
    Paginate the given data.

    :param data: The list of items to paginate
    :param page_param: The query parameter for the page number
    :param per_page_param: The query parameter for items per page
    :param default_page: The default page number if not provided
    :param default_per_page: The default number of items per page if not provided
    :return: A tuple containing paginated data, total count, page number, and items per page
    """
    try:
        page = int(request.args.get(page_param, default_page))
        per_page = int(request.args.get(per_page_param, default_per_page))

        if page < 1 or per_page < 1:
            raise ValueError("Page and per_page must be positive integers")

        total_items = len(data)
        start = (page - 1) * per_page
        end = start + per_page

        if start >= total_items:
            raise ValueError("Page number out of range")

        paginated_data = data[start:end]

        return paginated_data, total_items, page, per_page
    except ValueError as e:
        raise ValueError(str(e))
