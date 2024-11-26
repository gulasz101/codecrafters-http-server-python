import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn, _addr = server_socket.accept()  # wait for client

    match conn.recv(1024).decode("utf-8").split(" ")[1]:
        case "/":
            response = b"HTTP/1.1 200 OK\r\n\r\n"
        case _:
            response = b"HTTP/1.1 404 Not Found\r\n\r\n"

    conn.send(response)


if __name__ == "__main__":
    main()
