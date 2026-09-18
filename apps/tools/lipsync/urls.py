from django.urls import path
from apps.tools.lipsync import views

urlpatterns = [
    path('', views.lipsync_workspace_view, name='lipsync_workspace'),
    path('generate/', views.lipsync_generate_view, name='lipsync_generate'),
]
