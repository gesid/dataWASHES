from flask_restx import Namespace # type: ignore
from .logging_washes import log_request

def abort_execution(ns: Namespace, message: str, error_code: int) -> None:
    """
    Calls the function that properly abort the current request\n
    and creates the log for the request.
    """
    log_request(error_code)
    ns.abort(error_code, message=message, error_code=error_code)
