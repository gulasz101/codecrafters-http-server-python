import socket  # noqa: F401
import re


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn, _addr = server_socket.accept()  # wait for client

    request_uri = conn.recv(1024).decode("utf-8").split(" ")[1]
    if re.match("^/([a-zA-Z])*/([a-zA-Z])*", request_uri):
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
        print(response)
    else:
        response = b"HTTP/1.1 404 Not Found\r\n\r\n"

    conn.send(response)


if __name__ == "__main__":
    main()
