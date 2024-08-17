import logging
from flask import request
from datetime import datetime

logging.basicConfig(filename='access.log', level=logging.INFO, format='%(message)s')
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)

def log_request(status):
    log_details = {
        "ip": request.remote_addr,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "method": request.method,
        "route": request.full_path,
        "status": status
    }
    logging.info(log_details)
