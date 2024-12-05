from server.instance import server
import datetime

class DatabaseConn:

    @staticmethod
    def command(query, params=None, fetch=True):
        conn = server.getConn()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params or {})
                
                if not fetch:
                    conn.commit()
                    return

                rows = cur.fetchall()
                if len(rows) == 0:
                    return []

                columns = [desc[0] for desc in cur.description]
                results = [
                    {
                        column: (value.isoformat() if isinstance(value, datetime.datetime) else value)
                        for column, value in zip(columns, row)
                    }
                    for row in rows
                ]

                return results
        except Exception as e:
            raise Exception(f"Erro ao executar consulta: {str(e)}")
