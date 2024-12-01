import re
import socket  # noqa: F401
import sys
from threading import Thread

from http_server.http_utils.http_method import HttpMethod
import http_server.app.routes as routes
import http_server.http_utils.http_request as http_request


class REqual(str):
    "Override str.__eq__ to match a regex pattern."

    def __eq__(self, pattern):
        return bool(re.fullmatch(pattern, self))


def handle_connection(conn: socket.socket, directory=None):
    request = http_request.read_full_request(conn)
    request_method = http_request.read_request_method(request)
    request_body = http_request.read_request_body(request)
    request_uri = http_request.read_request_uri(request)
    request_header = http_request.read_request_headers(request)

    match REqual(request_uri):
        case r"^/$":
            response = b"HTTP/1.1 200 OK\r\n\r\n"
        case r"^/echo/(\S)*":
            response = routes.handle_echo(request_uri, request_header)
        case r"^/files/(\S)*":
            file_name = request_uri.split("/")[2]
            full_file_path = str(directory) + file_name
            match request_method:
                case HttpMethod.GET:
                    print("handling GET /files")
                    response = routes.handle_files_get(full_file_path)
                case HttpMethod.POST:
                    print("handling POST /files")
                    response = routes.handle_files_post(full_file_path, request_body)
        case r"^/user-agent$":
            response = routes.handle_user_agent(request_header)
        case r"^/([a-zA-Z])*/([a-zA-Z])*":
            response = routes.handle_any_any_request(request_uri)
        case _:
            response = b"HTTP/1.1 404 Not Found\r\n\r\n"

    conn.send(response)
    conn.close()


def bootstrap():
    directory = None
    try:
        for i in range(1, len(sys.argv)):
            if sys.argv[i] == "--directory":
                directory = sys.argv[int(i) + 1]
    except IndexError:
        pass
    print(("directory", directory))

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        conn, _addr = server_socket.accept()  # wait for client
        t = Thread(
            target=handle_connection,
            args=(
                conn,
                directory,
            ),
        )
        t.start()
