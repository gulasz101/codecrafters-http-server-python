import io
import gzip

from http_server.http_utils.http_header import HttpHeader


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


def handle_echo(request_uri: str, request_headers: dict[HttpHeader, str]) -> bytes:
    response_content = request_uri.split("/")[2].encode("utf-8")
    print(response_content)
    response_headers = {
        HttpHeader.CONTENT_TYPE: "text/plain",
        HttpHeader.CONTENT_LENGTH: str(len(response_content)),
    }
    if HttpHeader.ACCEPT_ENCODING in request_headers and "gzip" in request_headers[
        HttpHeader.ACCEPT_ENCODING
    ].split(", "):
        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode="wb") as gz:
            gz.write(response_content)

        response_content = buffer.getvalue()
        response_headers.update({HttpHeader.CONTENT_ENCODING: "gzip"})
        response_headers[HttpHeader.CONTENT_LENGTH] = str(len(response_content))

    print(response_content)
    formatted_headers = "\r\n".join(
        f"{key.value}: {value}" for key, value in response_headers.items()
    )

    return (
        f"HTTP/1.1 200 OK\r\n{formatted_headers}\r\n\r\n".encode("utf-8")
        + response_content
    )


def handle_user_agent(request_headers: dict[HttpHeader, str]) -> bytes:
    user_agent = request_headers[HttpHeader.USER_AGENT]

    formatted_headers = "\r\n".join(
        f"{key.value}: {value}"
        for key, value in {
            HttpHeader.CONTENT_TYPE: "text/plain",
            HttpHeader.CONTENT_LENGTH: len(user_agent),
        }.items()
    )

    return f"HTTP/1.1 200 OK\r\n{formatted_headers}\r\n\r\n{user_agent}".encode("utf-8")


def handle_any_any_request(request_uri: str) -> bytes:
    response_body = request_uri.split("/")[2]

    formatted_headers = "\r\n".join(
        f"{key.value}: {value}"
        for key, value in {
            HttpHeader.CONTENT_TYPE: "text/plain",
            HttpHeader.CONTENT_LENGTH: len(response_body),
        }.items()
    )

    return f"HTTP/1.1 200 OK\r\n{formatted_headers}\r\n\r\n{response_body}".encode(
        "utf-8"
    )
