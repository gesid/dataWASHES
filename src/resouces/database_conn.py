from server.instance import server
from flask import jsonify
from sqlalchemy import text


class DatabaseConn:
    
    @staticmethod
    def command(query, fetch=True):
        conn = server.getConn()

        try:
            with conn.connect() as conn:
                if not fetch:
                    conn.execute(text(query))
                    return
                
                result = conn.execute(text(query))
                rows = result.fetchall()
                columns = result.keys()
                results = [{column: value for column, value in zip(columns, row)} for row in rows]
                return jsonify(results)
        except Exception as e:
            return jsonify({'error': str(e)})