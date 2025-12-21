from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import logging

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>My Server</title></head>", "utf-8"))
        self.wfile.write(bytes("<body><p>This is a simple HTTP server.</p></body></html>", "utf-8"))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    with HTTPServer((hostName, serverPort), MyServer) as webServer:
        logging.info(f"Server started http://{hostName}:{serverPort}")

        try:
            webServer.serve_forever()
        except KeyboardInterrupt:
            pass

        webServer.server_close()
        logging.info("Server stopped.")