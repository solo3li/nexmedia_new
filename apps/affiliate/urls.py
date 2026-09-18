from django.urls import path
from apps.affiliate import views

urlpatterns = [
    path('', views.affiliate_dashboard_view, name='affiliate_dashboard'),
]
