from flask import Flask
from flask import request
from event_handler import ProcessEventHandler
import os
DATA_DIRECTORY = os.getcwd() + "\\server_files\\"
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/do_PROCESS_REQUEST', methods=['POST'])
def process_image():
    if request.method == 'POST':
        print('post method got')
        content_length = int(request.headers['Content-Length'])
        request_user = request.headers['username']
        request_pwd = request.headers['password']
        request_image = request.headers['image']
        request_method = request.headers['method']
        request_ip = request.headers['ip']
        body = request.data

        f = open(DATA_DIRECTORY + request_user + '_' + request_image, 'wb')
        f.write(body)
        f.close()

        process_event_handler = ProcessEventHandler()
        image_processed, lst_ret = process_event_handler.process(DATA_DIRECTORY + request_user + '_' + request_image,
                                                                 request_user)

        str_lst_ret = str(lst_ret)
        str_lst_ret_list = list(str_lst_ret)
        for i in range(1, len(str_lst_ret_list)):
            if str_lst_ret_list[i] == ',' and str_lst_ret_list[i - 1] == ']':
                str_lst_ret_list[i] = ';'

        str_lst_ret = "".join(str_lst_ret_list)
        response = str_lst_ret.encode()
        return response, 200
    else:
        print('Bad request sent')

