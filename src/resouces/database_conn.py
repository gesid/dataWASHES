from server.instance import Server
from flask import jsonify

class DatabaseConn:
    
    @staticmethod
    def command(query):
        server = Server()
        conn = server.getConn()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        results = [{column_name: column_value for column_name, column_value in zip([column[0] for column in cursor.description], row)} for row in rows]

        cursor.close()

        return jsonify(results)