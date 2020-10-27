# import tensorflow.compat.v1 as tf
# tf.disable_v2_behavior()
from PIL import Image
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
import cv2

import numpy as np
from django.views.generic import TemplateView
from keras.preprocessing.image import img_to_array

from resizeimage import resizeimage
from keras.models import load_model
# from keras.preprocessing.image import load_img
import logging

logger = logging.getLogger(__name__)


class MaskDetectionView(View):
    # template_name = 'mask.html'
    #
    # def get_context_data(self, *args, **kwargs):
    #     context = super(MaskDetectionView, self).get_context_data(*args, **kwargs)
    #     return context
    def post(self, request, *args, **kwargs):
        try:
            file_data = request.FILES.get('file')
            img = Image.open(file_data)
            model = load_model("mtcnn_face_mask.h5")
            # img_arr = np.array(img)
            # model = keras.models.load_model("mtcnn_face_mask.h5")
            cover = resizeimage.resize_cover(img, [160, 160], validate=False)
            x = []

            x = img_to_array(cover)

            x = np.expand_dims(x, axis=0)

            pred = model.predict(x)

            # print(pred[0][0])

            if pred[0][0] == 0.0:
                return JsonResponse({'status': 'success', 'message': 'MASK ON', 'data': {'color': 'green'}})

            elif pred[0][0] == 1.0:
                return JsonResponse({'status': 'success', 'message': 'No MASK Detected', 'data': {'color': 'red'}})

        except Exception as e:
            logger.exception('Exception {}'.format(e.args))
            return JsonResponse({'status': 'fail', 'message': 'Somehting went wrong. Please try again later'}, status=400)
