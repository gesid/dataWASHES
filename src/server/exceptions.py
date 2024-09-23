from flask import jsonify
import jwt
from werkzeug.exceptions import HTTPException
from server.instance import server

app = server.getApp()

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized access'}), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = jsonify({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

@app.errorhandler(jwt.exceptions.DecodeError)
def handle_jwt_decode_error(error):
    return jsonify({"error": "Invalid token", "message": str(error)}), 422

@app.errorhandler(Exception)
def handle_exception(error):
    response = jsonify({"error": "An unexpected error occurred", "message": str(error)})
    response.status_code = 500
    return response