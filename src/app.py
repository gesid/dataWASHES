from flask import make_response, render_template
from controllers import authors_ns, editions_ns, papers_ns, statistics_ns
from server import server
from api_utils import convert_to_csv


def main() -> None:
    server.api.add_namespace(editions_ns)
    server.api.add_namespace(papers_ns)
    server.api.add_namespace(authors_ns)
    server.api.add_namespace(statistics_ns)
    server.run()


@server.api.representation('text/csv')
def data_csv(data, code, headers):
    """Get result in csv"""
    resp = make_response(convert_to_csv(data), code)
    resp.headers.extend(headers)
    return resp


@server.app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    main()
