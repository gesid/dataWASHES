from server.instance import server
from flask import jsonify
from sqlalchemy import text

class DatabaseConn:
    
    @staticmethod
    def command(query, fetch=True, isJsonify=True):
        conn = server.getConn()
        
        try:
            with conn.connect() as conn:
                if not fetch:
                    conn.execute(text(query))
                    return
                
                result = conn.execute(text(query))
                rows = result.fetchall()
                if len(rows) == 0:
                    return []

                columns = result.keys()
                results = [{column: value for column, value in zip(columns, row)} for row in rows]
                if isJsonify:
                    return jsonify(results)
                return results
        except Exception as e:
            raise jsonify({'error': str(e)})
            