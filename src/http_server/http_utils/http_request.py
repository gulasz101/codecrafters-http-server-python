import socket

from http_server.http_utils.http_method import HttpMethod
from http_server.http_utils.http_header import HttpHeader


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
