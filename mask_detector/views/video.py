from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse, HttpResponseServerError
import cv2
import time

from django.views.decorators import gzip
import logging

logger = logging.getLogger(__name__)


class VideoCamera(object):
    def __init__(self):
        cam = 'https://stream:g10rjhRUFlo8ycNrrt2W@130.180.80.86:1448/axis-cgi/mjpg/video.cgi?&resolution=3840x2160'
        self.video = cv2.VideoCapture(cam)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret,image = self.video.read()
        ret,jpeg = cv2.imencode('.jpg',image)
        return jpeg.tobytes()


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@gzip.gzip_page
def index(request):
    try:
        return StreamingHttpResponse(gen(VideoCamera()),content_type="multipart/x-mixed-replace;boundary=frame")
    except HttpResponseServerError as he:
        logger.exception(str(he))
    except Exception as e:
        logger.exception(e.args)

    return HttpResponse('Error')
