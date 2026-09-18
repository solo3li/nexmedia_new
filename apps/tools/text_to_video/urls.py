from django.urls import path
from apps.tools.text_to_video import views

urlpatterns = [
    path('', views.text_to_video_workspace_view, name='text_to_video_workspace'),
    path('estimate/', views.text_to_video_estimate_view, name='text_to_video_estimate'),
    path('generate/', views.text_to_video_generate_view, name='text_to_video_generate'),
]
