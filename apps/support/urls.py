from django.urls import path
from apps.support import views

urlpatterns = [
    path('', views.ticket_list_view, name='ticket_list'),
    path('<uuid:ticket_id>/', views.ticket_detail_view, name='ticket_detail'),
]
