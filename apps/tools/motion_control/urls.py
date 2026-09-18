from django.urls import path
from apps.tools.motion_control import views

urlpatterns = [
    path('', views.motion_control_workspace_view, name='motion_control_workspace'),
    path('generate/', views.motion_control_generate_view, name='motion_control_generate'),
]
