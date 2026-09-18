from django.urls import path
from apps.content import views

urlpatterns = [
    path('blog/', views.blog_list_view, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail_view, name='blog_detail'),
    path('pages/<slug:slug>/', views.custom_page_view, name='custom_page'),
]
