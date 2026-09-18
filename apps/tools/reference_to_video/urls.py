from django.urls import path
from apps.tools.reference_to_video import views

urlpatterns = [
    path('', views.reference_to_video_workspace_view, name='reference_to_video_workspace'),
    path('generate/', views.reference_to_video_generate_view, name='reference_to_video_generate'),
]
