from django.urls import path
from apps.tools.stt import views

urlpatterns = [
    path('', views.stt_workspace_view, name='stt_workspace'),
    path('transcribe/', views.stt_transcribe_view, name='stt_transcribe'),
]
