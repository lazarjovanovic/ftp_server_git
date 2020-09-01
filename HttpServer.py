from http.server import BaseHTTPRequestHandler, HTTPServer
import os
FTP_DIRECTORY = os.getcwd() + "\\server_files\\"


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello from GET method!')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        request_user = self.headers['username']
        request_pwd = self.headers['password']
        request_image = self.headers['image']
        request_method = self.headers['method']
        request_ip = self.headers['ip']
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()

        f = open(FTP_DIRECTORY + request_user + '_' + request_image, 'wb')
        f.write(body)
        f.close()

        response = 'Image received, starting processing'.encode()
        self.wfile.write(response)


def start():
    print("HTTP Server started..")
    if not os.path.exists(FTP_DIRECTORY):
        os.mkdir(FTP_DIRECTORY)

    httpd = HTTPServer(('192.168.1.5', 8004), SimpleHTTPRequestHandler)
    httpd.serve_forever()
    print("HTTP Server stoped..")
