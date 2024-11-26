import socket  # noqa: F401
import re
from threading import Thread


class REqual(str):
    "Override str.__eq__ to match a regex pattern."

    def __eq__(self, pattern):
        return bool(re.fullmatch(pattern, self))


def handle_connection(conn):
    request = conn.recv(1024).decode("utf-8")
    request_uri = request.split(" ")[1]
    match REqual(request_uri):
        case r"^/$":
            response = b"HTTP/1.1 200 OK\r\n\r\n"
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


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        conn, _addr = server_socket.accept()  # wait for client
        t = Thread(target=handle_connection, args=(conn,))
        t.start()


if __name__ == "__main__":
    main()
