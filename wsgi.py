"""
WSGI entry point for the dataWASHES API.

Exposes the Flask application object to WSGI servers (e.g. gunicorn,
as configured in the ``Procfile``). Importing this module registers all
namespaces, the ``text/csv`` representation and the ``/dashboard`` route
that are defined in ``src/app.py``.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app import main  # noqa: E402  # pylint: disable=wrong-import-position
from server.instance import server  # noqa: E402  # pylint: disable=wrong-import-position

main()

app = server.app
