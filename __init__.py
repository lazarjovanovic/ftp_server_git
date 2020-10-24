from Server import app
import os
DATA_DIRECTORY = os.getcwd() + "\\server_files\\"


if __name__ == '__main__':
    if not os.path.exists(DATA_DIRECTORY):
        os.mkdir(DATA_DIRECTORY)
    print("Server started..")
    # app.run(host='192.168.1.5', port=8004, threaded=False)
    app.run(host='192.168.0.17', port=8004, threaded=False)
    print("Server stoped..")
