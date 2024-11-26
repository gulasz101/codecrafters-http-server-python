import socket  # noqa: F401
import re
from threading import Thread
import sys
import io


class REqual(str):
    "Override str.__eq__ to match a regex pattern."

    def __eq__(self, pattern):
        return bool(re.fullmatch(pattern, self))


def handle_connection(conn, directory=None):
    request = conn.recv(1024).decode("utf-8")
    request_uri = request.split(" ")[1]
    match REqual(request_uri):
        case r"^/$":
            response = b"HTTP/1.1 200 OK\r\n\r\n"
        case r"^/files/([a-zA-Z])*":
            file_name = request_uri.split("/")[2]

            try:
                file_handler = io.open(str(directory) + "/" + file_name)
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
        arg = sys.argv[1].strip("-").split("=")
        arg_name = arg[0]
        arg_value = arg[1]

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
