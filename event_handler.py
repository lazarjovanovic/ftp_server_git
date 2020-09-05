import os
from watchdog.events import RegexMatchingEventHandler
import json
from PIL import Image
from imageai.Detection.Custom import CustomObjectDetection
import pypyodbc as podbc
import datetime


class ProcessEventHandler(RegexMatchingEventHandler):
    FILES_REGEX = [r".*.jpg"]

    def __init__(self):
        super().__init__(self.FILES_REGEX)
        self.conn = podbc.connect(r'Driver={ODBC Driver 17 for SQL Server};Server=LAZAR-PC;Database=Derma_app_db;Trusted_Connection=yes;')

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
        # TODO: get detection with highest certainty - function
        highest_certainty = None
        highest_percentage = None
        if len(detections) == 0:
            highest_certainty = 'psoriasis_vulgaris'
            highest_percentage = 100

        # getting detected desease info from database
        cursor = self.conn.cursor()
        query = 'select * from Deseases where desease_name = \'' + highest_certainty + '\';'
        cursor.execute(query)
        data = cursor.fetchone()
        ret_dct = dict()
        ret_dct['desease'] = data[1]
        ret_dct['percentage'] = highest_percentage
        ret_dct['description'] = data[2]
        ret_dct['therapy'] = data[3]
        print('Detecting done')

        # logging detection information into database
        cursor = self.conn.cursor()
        time = str(datetime.datetime.now())
        query = 'insert into Requests values (\'' + str(user) + '\', \'' + time + '\',\'' + image_path_new + '\');'
        cursor.execute(query)
        self.conn.commit()

        return image_path_detected, ret_dct
