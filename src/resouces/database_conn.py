import datetime
from server.instance import server
from flask import jsonify
from sqlalchemy import text

class DatabaseConn:
    
    @staticmethod
    def command(query, params = None, fetch=True):
        conn = server.getConn()
        
        try:
            with conn.connect() as conn:
                if not fetch:
                    conn.execute(text(query), params or {})
                    return
                
                result = conn.execute(text(query), params or {})
                rows = result.fetchall()
                if len(rows) == 0:
                    return []

                columns = result.keys()
                results = [{column: (value.isoformat() if isinstance(value, datetime.datetime) else value) for column, value in zip(columns, row)} for row in rows]
                return results
        except Exception as e:
            raise jsonify({'error': str(e)})
            