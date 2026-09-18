from django.urls import path
from apps.tools.text_to_image import views

urlpatterns = [
    path('', views.text_to_image_workspace_view, name='text_to_image_workspace'),
    path('generate/', views.text_to_image_generate_view, name='text_to_image_generate'),
]
