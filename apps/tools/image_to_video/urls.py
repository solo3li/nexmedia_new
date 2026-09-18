from django.urls import path
from apps.tools.image_to_video import views

urlpatterns = [
    path('', views.image_to_video_workspace_view, name='image_to_video_workspace'),
    path('generate/', views.image_to_video_generate_view, name='image_to_video_generate'),
]
