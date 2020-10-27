import requests

from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse, HttpResponseServerError
import cv2
import time

from django.views.decorators import gzip
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning
import ssl
import logging

logger = logging.getLogger(__name__)


class VideoCamera(object):
    # def __init__(self):
    #     self.video = cv2.VideoCapture('http://43.251.80.161:83/cgi-bin/camera?resolution=640&amp;quality=1&amp;Language=0&amp;1591237146')
    #
    # def __del__(self):
    #     self.video.release()

    def get_frame(self):
        # cam2 = 'https://www.sample-videos.com/video/mp4/720/big_buck_bunny_720p_2mb.mp4'
        # ssl.match_hostname = lambda cert, hostname: hostname == cert['subjectAltName'][0][1]
        # requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        # cam2 = "https://130.180.80.86:1448/axis-cgi/jpg/image.cgi?&resolution=3840x2160"
        # cam2 = 'http://43.251.80.161:83/cgi-bin/camera'
        cam2 = "https://stream:g10rjhRUFlo8ycNrrt2W@130.180.80.86:1448/axis-cgi/jpg/image.cgi?&resolution=3840x2160"
        # cam2 = "http://localhost:8090/cam2.mjpeg"
        response = requests.get(cam2, stream=True, verify='cert.pem')


        # response = requests.get(cam2, auth=HTTPBasicAuth('stream', 'g10rjhRUFlo8ycNrrt2W'), stream=True, verify='/Users/rajkumar/Downloads/cert (1).pem')
        # response.raw.decode_content = True
        stream = response.content
        return stream
        # ret,image = self.video.read()
        # ret,jpeg = cv2.imencode('.jpg',image)
        # return jpeg.tobytes()


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@gzip.gzip_page
def stream_video(request):
    try:
        return StreamingHttpResponse(gen(VideoCamera()),content_type="multipart/x-mixed-replace;boundary=frame")
    except HttpResponseServerError as he:
        logger.exception(str(he))
    except Exception as e:
        logger.exception(e.args)
