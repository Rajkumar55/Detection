from PIL import Image
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.generic.base import View
import cv2 as cv
import argparse
import sys
import numpy as np
import os.path
import logging

from keras_preprocessing.image import img_to_array

logger = logging.getLogger(__name__)


class LicensePlateDetectionView(View):
    # Initialize the parameters
    confThreshold = 0.5  # Confidence threshold
    nmsThreshold = 0.4  # Non-maximum suppression threshold

    inpWidth = 416  # 608     #Width of network's input image
    inpHeight = 416  # 608     #Height of network's input image

    # Load names of classes
    classesFile = "classes.names"

    classes = None
    with open(classesFile, 'rt') as f:
        classes = f.read().rstrip('\n').split('\n')

    # Give the configuration and weight files for the model and load the network using them.

    modelConfiguration = "darknet-yolov3.cfg"
    modelWeights = "lapi.weights"

    net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
    net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

    # Get the names of the output layers
    def getOutputsNames(self, net):
        # Get the names of all the layers in the network
        layersNames = net.getLayerNames()
        # Get the names of the output layers, i.e. the layers with unconnected outputs
        return [layersNames[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

    # Draw the predicted bounding box
    def drawPred(self, frame, classId, conf, left, top, right, bottom):
        # Draw a bounding box.
        #    cv.rectangle(frame, (left, top), (right, bottom), (255, 178, 50), 3)
        cv.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)

        label = '%.2f' % conf

        # Get the label for the class name and its confidence
        if self.classes:
            assert (classId < len(self.classes))
            label = '%s:%s' % (self.classes[classId], label)

        # Display the label at the top of the bounding box
        labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        top = max(top, labelSize[1])
        cv.rectangle(frame, (left, top - round(1.5 * labelSize[1])), (left + round(1.5 * labelSize[0]), top + baseLine),
                     (0, 0, 255), cv.FILLED)
        # cv.rectangle(frame, (left, top - round(1.5*labelSize[1])), (left + round(1.5*labelSize[0]), top + baseLine),    (255, 255, 255), cv.FILLED)
        cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)

    # Remove the bounding boxes with low confidence using non-maxima suppression
    def postprocess(self, frame, outs):
        frameHeight = frame.shape[0]
        frameWidth = frame.shape[1]

        classIds = []
        confidences = []
        boxes = []
        # Scan through all the bounding boxes output from the network and keep only the
        # ones with high confidence scores. Assign the box's class label as the class with the highest score.
        classIds = []
        confidences = []
        boxes = []
        for out in outs:
            print("out.shape : ", out.shape)
            for detection in out:
                # if detection[4]>0.001:
                scores = detection[5:]
                classId = np.argmax(scores)
                # if scores[classId]>confThreshold:
                confidence = scores[classId]
                if detection[4] > self.confThreshold:
                    print(detection[4], " - ", scores[classId], " - th : ", self.confThreshold)
                    print(detection)
                if confidence > self.confThreshold:
                    center_x = int(detection[0] * frameWidth)
                    center_y = int(detection[1] * frameHeight)
                    width = int(detection[2] * frameWidth)
                    height = int(detection[3] * frameHeight)
                    left = int(center_x - width / 2)
                    top = int(center_y - height / 2)
                    classIds.append(classId)
                    confidences.append(float(confidence))
                    boxes.append([left, top, width, height])

        # Perform non maximum suppression to eliminate redundant overlapping boxes with
        # lower confidences.
        indices = cv.dnn.NMSBoxes(boxes, confidences, self.confThreshold, self.nmsThreshold)
        for i in indices:
            i = i[0]
            box = boxes[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]
            self.drawPred(frame, classIds[i], confidences[i], left, top, left + width, top + height)

    def post(self, request, *args, **kwargs):
        try:
            file_data = request.FILES.get('file')
            img = Image.open(file_data)
            # frame = img_to_array(img)
            im_pillow = np.array(img)
            frame = cv.cvtColor(im_pillow, cv.COLOR_RGB2BGR)

            # Process inputs
            # winName = 'Deep learning object detection in OpenCV'
            # cv.namedWindow(winName, cv.WINDOW_NORMAL)

            # cap = cv.VideoCapture(args.image)
            outputFile = 'output.jpg'

            # Create a 4D blob from a frame.
            blob = cv.dnn.blobFromImage(frame, 1 / 255, (self.inpWidth, self.inpHeight), [0, 0, 0], 1, crop=False)

            # Sets the input to the network
            self.net.setInput(blob)

            # Runs the forward pass to get output of the output layers
            outs = self.net.forward(self.getOutputsNames(self.net))

            # Remove the bounding boxes with low confidence
            self.postprocess(frame, outs)

            # Put efficiency information. The function getPerfProfile returns the overall time for inference(t) and the timings for each of the layers(in layersTimes)
            t, _ = self.net.getPerfProfile()
            label = 'Inference time: %.2f ms' % (t * 1000.0 / cv.getTickFrequency())
            # cv.putText(frame, label, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))

            # Write the frame with the detection boxes
            cv.imwrite('media/' + outputFile, frame.astype(np.uint8))
            return JsonResponse({'status': 'success', 'message': 'License Plate Detected', 'data': settings.MEDIA_URL + outputFile})
            # pil_img = Image.fromarray(frame)
            # response = HttpResponse(content_type="image/png")
            # pil_img.save(response, "PNG")
            # return response
            # return JsonResponse({'status': 'success', 'message': 'License Plate Detected'})

        except Exception as e:
            logger.exception('Exception {}'.format(e.args))
            return JsonResponse({'status': 'fail', 'message': 'Something went wrong. Please try again later'},
                                status=500)
