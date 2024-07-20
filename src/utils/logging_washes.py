import logging
from flask import request
from datetime import datetime

logging.basicConfig(filename='access.log', level=logging.INFO, format='%(message)s')
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)

def log_request(method, route, status):
    log_details = {
        "ip": request.remote_addr,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "method": method,
        "route": route,
        "status": status
    }
    logging.info(log_details)
