from http.server import BaseHTTPRequestHandler, HTTPServer


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello from GET method!')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()

        f = open('D:\\pristiglaSlikaANDROID.jpg', 'wb')
        f.write(body)
        f.close()

        response = 'Sljaka bebicaaaaaa!!!!'.encode()
        self.wfile.write(response)


def start():
    print("HTTP Server started..")
    httpd = HTTPServer(('192.168.0.12', 8004), SimpleHTTPRequestHandler)
    httpd.serve_forever()
    print("HTTP Server stoped..")


start()
