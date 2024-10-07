from django.urls import path
from . import views

urlpatterns = [
    path("download", views.download_video, name="download"),
    path("video-info", views.get_video_info, name="video-info"),
]
