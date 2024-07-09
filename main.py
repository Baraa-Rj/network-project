from socket import *
import urllib.parse

def get_content_type(file_path):
    if file_path.endswith(".html"):
        return "text/html"
    elif file_path.endswith(".css"):
        return "text/css"
    elif file_path.endswith(".png"):
        return "image/png"
    elif file_path.endswith(".jpg"):
        return "image/jpeg"
    return "application/octet-stream"

def parse_query(query):
    # Parse query parameters from the URL
    parameters = urllib.parse.parse_qs(query)
    return {k: v[0] for k, v in parameters.items()}

# Server setup
serverPort = 6060
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(5)
print("Server is ready!")

while True:
    connectionSocket, addr = serverSocket.accept()
    request = connectionSocket.recv(1024).decode()
    print(f"Received HTTP request from {addr}:\n{request}")

    try:
        # Parse the request line
        request_line = request.splitlines()[0]
        request_type, path_and_query, _ = request_line.split()
        path, _, query = path_and_query.partition('?')
        file_path = urllib.parse.unquote(path[1:])  # Remove the leading '/'

        # Parse query parameters
        params = parse_query(query)

        if file_path == "so":
            connectionSocket.send(
                "HTTP/1.1 307 Temporary Redirect\r\nLocation: https://stackoverflow.com\r\n\r\n".encode())
        elif file_path == "itc":
            connectionSocket.send(
                "HTTP/1.1 307 Temporary Redirect\r\nLocation: https://itc.birzeit.edu\r\n\r\n".encode())
        elif file_path == "display-image" and 'imagename' in params:
            image_name = params['imagename']
            image_path = f"images/{image_name}"
            try:
                with open(image_path, "rb") as image_file:
                    response_header = (
                        "HTTP/1.1 200 OK\r\n"
                        f"Content-Type: {content_type}\r\n"
                        "Connection: close\r\n\r\n"
                    )
                    connectionSocket.send(response_header.encode())
                    connectionSocket.send(image_file.read())
            except FileNotFoundError:
                error_response = """HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n
                                    <html><head><title>Error 404</title></head>
                                    <body><h2 style="color: red;">Image not found!</h2></body></html>"""
                connectionSocket.send(error_response.encode())
        else:
            if file_path in ["", "index.html", "test.html", "en"]:
                file_path = "test.html"
            elif file_path == "ar":
                file_path = "testAr.html"

            content_type = get_content_type(file_path)
            try:
                with open(file_path, "rb") as f:
                    response_header = (
                        "HTTP/1.1 200 OK\r\n"
                        f"Content-Type: {content_type}\r\n"
                        "Connection: close\r\n\r\n"
                    )
                    connectionSocket.send(response_header.encode())
                    connectionSocket.send(f.read())
            except FileNotFoundError:
                error_response = """HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n
                                    <html><head><title>Error 404</title></head>
                                    <body><h2 style="color: red;">The file is not found!</h2></body></html>"""
                connectionSocket.send(error_response.encode())
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        connectionSocket.close()
