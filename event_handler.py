import os
from watchdog.events import RegexMatchingEventHandler
import json
from PIL import Image
#from imageai.Detection.Custom import CustomObjectDetection


class ProcessEventHandler(RegexMatchingEventHandler):
    FILES_REGEX = [r".*.txt"]

    def __init__(self):
        super().__init__(self.FILES_REGEX)

    def on_created(self, event):
        self.process(event)

    def process(self, event):
        request_path = event.src_path
        path_parts = request_path.split('\\')
        dir_path = ''
        for i in range(len(path_parts)-1):
            dir_path += path_parts[i] + '\\'
        with open(request_path) as json_file:
            data = json.load(json_file)
        image_path = dir_path + data['image']
        image_path_new = image_path.split('.')[0] + '.png'
        image_path_detected = image_path.split('.')[0] + '_detected.png'

        im = Image.open(image_path)
        im.thumbnail(im.size, Image.ANTIALIAS)
        im.save(image_path_new)
        os.remove(image_path)
        im.close()

        # TODO: RUN OBJECT DETECTION AND FORMAT OUTPUT
        # detector = CustomObjectDetection()
        # detector.setModelTypeAsYOLOv3()
        # detector.setModelPath("detection_model-ex-013--loss-0015.740.h5")
        # detector.setJsonPath("detection_config.json")
        # detector.loadModel()
        # detections = detector.detectObjectsFromImage(input_image=image_path_new, output_image_path=image_path_detected)
        # for detection in detections:
        #     print(detection["name"], " : ", detection["percentage_probability"], " : ", detection["box_points"])
        # TODO: MOVE IMAGE TO PROCESSED IMAGES
        # TODO: STORE REQUEST TO DATABASE
        # TODO: GET THE OUTPUT IN ANDROID
