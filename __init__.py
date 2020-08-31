from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.filesystems import AbstractedFS
from watchdog.observers import Observer
from event_handler import ProcessEventHandler
import logging
import time
import os
import shutil
import datetime
import time
import _thread
import ftplib

FTP_PORT = 2121  # The port the FTP server will listen on. This must be greater than 1023 unless you run this script as root.
FTP_USER = "derma_app_user"  # The name of the FTP user that can log in.
FTP_PASSWORD = "derma_pass_123"  # The FTP user's password.
FTP_DIRECTORY = os.getcwd() + "\\server_files\\"  # The directory the FTP user will have full read/write access to.


def main():
    if not os.path.exists(FTP_DIRECTORY):
        os.mkdir(FTP_DIRECTORY)

    starting_time = str(datetime.datetime.now())
    active_path = FTP_DIRECTORY
    if not os.path.exists(active_path):
        os.mkdir(active_path)

    absfs = AbstractedFS(active_path, cmd_channel=1)

    authorizer = DummyAuthorizer()

    authorizer.add_user(FTP_USER, FTP_PASSWORD, active_path, perm='elradfmw')  # Define a new user having full r/w permissions.

    handler = FTPHandler
    handler.authorizer = authorizer

    handler.banner = "Client connected"  # Define a customized banner (string returned when client connects)

    # Optionally specify range of ports to use for passive connections.
    handler.passive_ports = range(50000, 65535)

    #address = ('', FTP_PORT)
    address = ('192.168.1.5', 8004)
    server = FTPServer(address, handler)

    server.max_cons = 256
    server.max_cons_per_ip = 5

    # server.serve_forever()  # blocking server execution

    _thread.start_new_thread(server.serve_forever, tuple())

    folder_size = len(os.listdir(active_path))

    # watchdog
    process_event_handler = ProcessEventHandler()
    observer = Observer()
    observer.schedule(process_event_handler, active_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

    # while True:
    #     files_in_folder = os.listdir(active_path)
    #     if len(files_in_folder) > folder_size:
    #         print('New files arrived')
    #         folder_size = len(files_in_folder)
    #     else:
    #         print('So far no new files')
    #     time.sleep(60)


if __name__ == '__main__':
    print("FTP server started")
    main()
    print("FTP server closed")
