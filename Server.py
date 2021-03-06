import json

from flask import Flask
from flask import jsonify
from flask import request
from event_handler import ProcessEventHandler
import os
DATA_DIRECTORY = os.getcwd() + "\\server_files\\"
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/do_GET_PROCESSED', methods=['POST'])
def get_processed():
    if request.method == 'POST':
        print('post method got')
        request_user = request.headers['username']
        body = request.form['query']
        query = body + "\'" + request_user + "\';"

        process_event_handler = ProcessEventHandler()
        # lst_images, lst_data = process_event_handler.get_processed_imges(query)
        json_ret = process_event_handler.get_processed_imges(query)

        # response = str([lst_images, lst_data]).encode()
        # response_data = str(lst_data).encode()
        # response_images = bytearray()
        # for item in lst_images:
        #     response_images += 'image'.encode() + item
        # response = response_data + response_images
        response = json_ret
        # return response, 200
        return jsonify(response), 200
    else:
        print('Bad request sent')


@app.route('/do_PROCESS_REQUEST', methods=['POST'])
def process_image():
    if request.method == 'POST':
        print('post method got')
        request_user = request.headers['username']
        request_image = request.headers['image']
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


@app.route('/do_REGISTER_USER', methods=['POST'])
def register_user():
    if request.method == 'POST':
        body = request.data
        data = json.loads(body)
        print(data)
        process_event_handler = ProcessEventHandler()
        hashValue = process_event_handler.register_user(data['username'], data['email'], data['password'])
        response = hashValue.encode()
        return response, 200
    else:
        print('Bad request sent')
