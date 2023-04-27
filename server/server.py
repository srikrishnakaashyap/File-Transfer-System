import socket
import os
import shutil


def cleanup(client_dir):
    """Delete the client's private directory."""
    shutil.rmtree(client_dir)


def process():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)

    print(f"Server listening on port {PORT}")

    while True:
        conn, addr = server_socket.accept()
        print(f"Connection established with {addr}")
        authenticated = False

        while not authenticated:
            data = conn.recv(1024).decode("utf-8")
            if not data:
                break

            username, password = data.split()

            print("USERNAME", username)
            print("PASSWORD", password)

            if username == USERNAME and password == PASSWORD:
                authenticated = True
                client_dir = f"{username}_dir"

                if not os.path.exists(client_dir):
                    os.makedirs(client_dir)

                conn.sendall("Authentication successful".encode("utf-8"))
            else:
                conn.sendall("Authentication failed".encode("utf-8"))

            print("Authenticated", authenticated)

        if authenticated:
            while True:
                data = conn.recv(1024).decode("utf-8")
                if not data:
                    break

                command = data.split()[0]
                args = data.split()[1:]

                if command == "ls":
                    response = "\n".join(os.listdir("."))
                elif command == "cd":
                    try:
                        os.chdir(args[0])
                        response = "Directory changed"
                    except:
                        response = "Unable to change directory"
                elif command == "pwd":
                    response = os.getcwd().replace(client_dir, "", 1)
                elif command == "get":
                    try:
                        filename = args[0]
                        filepath = os.path.join(client_dir, filename)
                        filesize = os.path.getsize(filepath)
                        with open(filepath, "rb") as f:
                            conn.sendall(f"file:{filename}:{filesize}".encode("utf-8"))
                            while True:
                                chunk = f.read(1024)
                                if not chunk:
                                    break
                                conn.sendall(chunk)
                    except:
                        response = "Unable to get file"
                else:
                    response = "Unknown command"

                conn.sendall(response.encode("utf-8"))

            cleanup(client_dir)

        conn.close()


if __name__ == "__main__":
    global HOST
    global PORT
    global USERNAME
    global PASSWORD

    HOST = "localhost"
    PORT = 12345
    USERNAME = "admin"
    PASSWORD = "password"

    process()