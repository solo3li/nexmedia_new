from django.urls import path
from apps.tools.avatar_video import views

urlpatterns = [
    path('', views.avatar_video_workspace_view, name='avatar_video_workspace'),
    path('generate/', views.avatar_video_generate_view, name='avatar_video_generate'),
]
