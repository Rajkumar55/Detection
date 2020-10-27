"""MaskDetection URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from mask_detector.views import MaskDetectionView
from mask_detector.views.external_cam import stream_video
from mask_detector.views.license_detection import LicensePlateDetectionView
from mask_detector.views.video import index
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('detect-mask/', csrf_exempt(MaskDetectionView.as_view())),
    path('', TemplateView.as_view(template_name='mask.html')),
    path('video/', index),
    path('video/external/', stream_video),
    path('detect/license-plate/', csrf_exempt(LicensePlateDetectionView.as_view())),
    path('license/', TemplateView.as_view(template_name='license_plate.html')),
]

urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
