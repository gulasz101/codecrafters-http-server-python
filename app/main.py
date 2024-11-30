import io
import re
import socket  # noqa: F401
import sys
from enum import Enum
from threading import Thread

import gzip


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"


class REqual(str):
    "Override str.__eq__ to match a regex pattern."

    def __eq__(self, pattern):
        return bool(re.fullmatch(pattern, self))


def handle_files_get(full_file_path: str):
    try:
        file_handler = io.open(full_file_path)
        file_contents = file_handler.read()

        response = "\r\n".join(
            [
                "HTTP/1.1 200 OK",
                "Content-Type: application/octet-stream\r\nContent-Length: "
                + str(file_contents.__len__())
                + "\r\n",
                file_contents,
            ]
        ).encode("utf-8")

    except IOError:
        response = b"HTTP/1.1 404 Not Found\r\n\r\n"

    return response


def handle_files_post(full_file_path: str, request_body: str) -> bytes:
    try:
        file_handler = io.open(full_file_path, "w")
        file_handler.write(request_body)

        file_handler.close()
        response = b"HTTP/1.1 201 Created\r\n\r\n"

    except IOError:
        response = b"HTTP/1.1 400 Bad Request\r\n\r\n"

    return response


def read_full_request(conn: socket.socket) -> str:
    MSGLEN = 1024
    chunks = []
    bytes_received = 0
    while True:
        chunk = conn.recv(MSGLEN)
        if chunk == b"":
            raise RuntimeError("socket connection broken")

        chunks.append(chunk.decode("utf-8"))

        bytes_received = len(chunk)

        if bytes_received < MSGLEN:
            break
    return "".join(chunks)


def read_request_method(request: str) -> HttpMethod:
    try:
        return HttpMethod(request.split(" ")[0])
    except ValueError:
        raise ValueError("Invalid request method")


def read_request_uri(request: str) -> str:
    return request.split(" ")[1]


def read_request_body(request: str) -> str:
    return request.split("\r\n").pop()


class HttpHeader(Enum):
    CONTENT_TYPE = "Content-Type"
    CONTENT_LENGTH = "Content-Length"
    CONTENT_ENCODING = "Content-Encoding"
    USER_AGENT = "User-Agent"
    ACCEPT = "Accept"
    ACCEPT_ENCODING = "Accept-Encoding"


def read_request_headers(request: str) -> dict[HttpHeader, str]:
    headers = {}

    for line in request.split("\r\n"):
        if ": " in line:
            key, value = line.split(": ")
            try:
                header = HttpHeader(key)
                headers[header] = value
            except ValueError:
                # ignore as it is not header
                continue
    return headers


def handle_connection(conn: socket.socket, directory=None):
    request = read_full_request(conn)
    request_method = read_request_method(request)
    request_body = read_request_body(request)
    request_uri = read_request_uri(request)
    request_header = read_request_headers(request)

    match REqual(request_uri):
        case r"^/$":
            response = b"HTTP/1.1 200 OK\r\n\r\n"
        case r"^/echo/(\S)*":
            response_content = request_uri.split("/")[2].encode("utf-8")
            response_headers = {
                HttpHeader.CONTENT_TYPE: "text/plain",
                HttpHeader.CONTENT_LENGTH: str(response_content.__len__()),
            }
            if (
                HttpHeader.ACCEPT_ENCODING in request_header
                and "gzip" in request_header[HttpHeader.ACCEPT_ENCODING].split(", ")
            ):
                response_content = gzip.compress(response_content)
                response_headers.update({HttpHeader.CONTENT_ENCODING: "gzip"})

            response = (
                "\r\n".join(
                    [
                        "HTTP/1.1 200 OK",
                        "".join(
                            f"{key.value}: {value}\r\n"
                            for key, value in response_headers.items()
                        )
                        + "\r\n",
                    ]
                ).encode("utf-8")
                + response_content
            )

        case r"^/files/(\S)*":
            file_name = request_uri.split("/")[2]
            full_file_path = str(directory) + file_name
            match request_method:
                case HttpMethod.GET:
                    print("handling GET /files")
                    response = handle_files_get(full_file_path)
                case HttpMethod.POST:
                    print("handling POST /files")
                    response = handle_files_post(full_file_path, request_body)
        case r"^/user-agent$":
            request_pieces = request.split("\r\n")
            # unset unwanted parts
            request_pieces.pop()
            request_pieces.pop()
            request_pieces.pop(0)
            request_pieces = map(lambda x: x.split(" "), request_pieces)
            user_agent = dict(request_pieces)["User-Agent:"]

            response = "\r\n".join(
                [
                    "HTTP/1.1 200 OK",
                    "Content-Type: text/plain\r\nContent-Length: "
                    + str(user_agent.__len__())
                    + "\r\n",
                    user_agent,
                ]
            ).encode("utf-8")
        case r"^/([a-zA-Z])*/([a-zA-Z])*":
            response_body = request_uri.split("/")[2]
            response = "\r\n".join(
                [
                    "HTTP/1.1 200 OK",
                    "Content-Type: text/plain\r\nContent-Length: "
                    + str(response_body.__len__())
                    + "\r\n",
                    response_body,
                ]
            ).encode("utf-8")
        case _:
            response = b"HTTP/1.1 404 Not Found\r\n\r\n"

    conn.send(response)
    conn.close()


def main():
    directory = None
    try:
        arg_name = sys.argv[1].strip("-")
        arg_value = sys.argv[2]

        print(
            (
                arg_name,
                arg_value,
            )
        )

        if arg_name != "directory":
            raise NameError("Unknown argument")
        directory = arg_value
    except IndexError:
        pass

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


if __name__ == "__main__":
    main()
