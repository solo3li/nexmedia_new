from django.urls import path
from apps.tools.tts import views

urlpatterns = [
    path('', views.tts_workspace_view, name='tts_workspace'),
    path('estimate/', views.tts_estimate_view, name='tts_estimate'),
    path('generate/', views.tts_generate_view, name='tts_generate'),
]
