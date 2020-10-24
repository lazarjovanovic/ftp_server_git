import os
import io
from watchdog.events import RegexMatchingEventHandler
import json
from PIL import Image
from imageai.Detection.Custom import CustomObjectDetection
import pyodbc
import pyodbc as podbc
import datetime
# import pypyodbc as pyodbc


class ProcessEventHandler(RegexMatchingEventHandler):
    FILES_REGEX = [r".*.jpg"]

    def __init__(self):
        super().__init__(self.FILES_REGEX)
        self.conn = podbc.connect(r'Driver={ODBC Driver 17 for SQL Server};Server=LAZAR-PC;Database=Derma_app_db;Trusted_Connection=yes;')
        # self.conn = pyodbc.connect('Driver={SQL Server};'
        #                            'Server=LAPTOP-KTQV5DSC;'
        #                            'Database=Derma_app_db;'
        #                            'Trusted_Connection=yes;')

    # def on_created(self, event):
    #     self.process(event)

    def process_image(self, image_path_new, image_path_detected):
        detector = CustomObjectDetection()
        detector.setModelTypeAsYOLOv3()
        detector.setModelPath("detection_model-ex-013--loss-0015.740.h5")
        detector.setJsonPath("detection_config.json")
        detector.loadModel()
        detections = detector.detectObjectsFromImage(input_image=image_path_new, output_image_path=image_path_detected)
        print(str(len(detections)) + ' on image')
        for detection in detections:
            print(detection["name"], " : ", detection["percentage_probability"], " : ", detection["box_points"])
        return detections

    def process(self, path, user):
        image_path = path
        image_path_new = image_path.split('.')[0] + '.png'
        image_path_detected = image_path.split('.')[0] + '_detected.png'

        if image_path != image_path_new:
            im = Image.open(image_path)
            im.thumbnail(im.size, Image.ANTIALIAS)
            im.save(image_path_new)
            os.remove(image_path)
            im.close()

        # running object detection
        print('Start detecting')
        detections = self.process_image(image_path_new, image_path_detected)
        # TODO: get top 3 detections with certainty higher than 50% and sort it
        list_certainities = list()
        # tmp here
        if len(detections) == 0:
            highest_certainty = 'psoriasis_vulgaris'
            highest_percentage = 100
            tmp_dct = dict()
            tmp_dct['desease'] = highest_certainty
            tmp_dct['percentage'] = highest_percentage
            list_certainities.append(tmp_dct)
            tmp_dct = dict()
            tmp_dct['desease'] = 'second'
            tmp_dct['percentage'] = 22
            list_certainities.append(tmp_dct)

        # getting detected desease info from database
        list_ret = list()
        str_detections = ''
        for i in range(len(list_certainities)):
            cursor = self.conn.cursor()
            query = 'select * from Deseases where desease_name = \'' + list_certainities[i]['desease'] + '\';'
            cursor.execute(query)
            data = cursor.fetchone()
            if i == 0:
                pom_lst = [list_certainities[i]['desease'], str(list_certainities[i]['percentage']), data[2], data[3]]
            else:
                pom_lst = [list_certainities[i]['desease'], str(list_certainities[i]['percentage'])]
            str_detections += str(list_certainities[i]['desease']) + ' ' + str(list_certainities[i]['percentage']) + ';'
            list_ret.append(pom_lst)
        str_detections = str_detections[:-1]
        print('Detecting done')

        # logging detection information into database
        cursor = self.conn.cursor()
        time = str(datetime.datetime.now())
        query = 'insert into Requests values (\'' + str(
            user) + '\', \'' + time + '\',\'' + image_path_new + '\', \'' + str_detections + '\');'
        cursor.execute(query)
        self.conn.commit()

        return image_path_detected, list_ret

    def image_to_byte_array(self, image):
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format=image.format)
        imgByteArr = imgByteArr.getvalue()
        return imgByteArr

    def get_processed_imges(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        dct_data = dict()
        for item in data:
            key = item[2]
            tmp_dct = dict()
            tmp_dct['path'] = item[3]
            tmp_dct['deseases'] = item[4]
            dct_data[key] = tmp_dct
        dct_data = dict(sorted(dct_data.items()))
        dct_data_work = dict()
        for key in list(reversed(list(dct_data)))[0:5]:
            dct_data_work[key] = dct_data[key]
        lst_images = list()
        lst_data = list()
        for key in dct_data_work:
            im = Image.open(open(dct_data_work[key]['path'], 'rb'))
            im_bytes = self.image_to_byte_array(im)
            lst_images.append(im_bytes)
            list_certainities = list()
            deseases = dct_data_work[key]['deseases']
            deseases_parts = deseases.split(';')
            for d in deseases_parts:
                d_parts = d.split(' ')
                dct = {'desease': d_parts[0], 'percentage': d_parts[1]}
                list_certainities.append(dct)

            lst_one = list()
            for i in range(len(list_certainities)):
                cursor = self.conn.cursor()
                query = 'select * from Deseases where desease_name = \'' + list_certainities[i]['desease'] + '\';'
                cursor.execute(query)
                data = cursor.fetchone()
                if i == 0:
                    pom_lst = [list_certainities[i]['desease'], str(list_certainities[i]['percentage']), data[2],
                               data[3]]
                else:
                    pom_lst = [list_certainities[i]['desease'], str(list_certainities[i]['percentage'])]
                lst_one.append(pom_lst)
            lst_data.append(lst_one)

        list_ret = list()
        for i in range(len(lst_data)):
            pom_dct = dict()
            for j in range(len(lst_data[i])):
                pom_dct[str(j)] = lst_data[i][j]
                pom_dct['img'] = lst_images[i]
                list_ret.append(pom_dct)

        # return lst_images, lst_data
        # json_ret = json.dumps(list_ret)
        return list_ret

    def register_user(self, username, email, password):
        cursor = self.conn.cursor()
        query = 'SELECT Count(*) FROM [Users] WHERE [username] = \'' + username + '\' OR [email] = \'' + email + '\''
        cursor.execute(query)
        data = cursor.fetchone()

        if data[0] == 0:
            hashValue = str(hash(username))
            cursor = self.conn.cursor()
            query = 'INSERT INTO [Users] VALUES (\'' + username + '\', \'' + password + '\', \'' + email + '\',\'' + hashValue + '\')'
            cursor.execute(query)
            self.conn.commit()
            return hashValue
        else:
            return ''
