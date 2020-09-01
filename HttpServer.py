from http.server import BaseHTTPRequestHandler, HTTPServer
from event_handler import ProcessEventHandler
from watchdog.observers import Observer
import time
import _thread
import os
DATA_DIRECTORY = os.getcwd() + "\\server_files\\"


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_CONNECT(self):
        self.send_response(200, "HTTP/1.1")
        self.end_headers()
        self.wfile.write(b'Connection')

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

        f = open(DATA_DIRECTORY + request_user + '_' + request_image, 'wb')
        f.write(body)
        f.close()

        response = 'Image received, starting processing'.encode()
        self.wfile.write(response)


def start():
    print("HTTP Server started..")
    if not os.path.exists(DATA_DIRECTORY):
        os.mkdir(DATA_DIRECTORY)

    httpd = HTTPServer(('192.168.1.5', 8004), SimpleHTTPRequestHandler)
    # httpd.serve_forever()
    _thread.start_new_thread(httpd.serve_forever, tuple())

    # watchdog
    process_event_handler = ProcessEventHandler()
    observer = Observer()
    observer.schedule(process_event_handler, DATA_DIRECTORY, recursive=True)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

    print("HTTP Server stoped..")
