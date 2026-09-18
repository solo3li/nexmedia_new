from django.urls import path
from apps.billing import views

urlpatterns = [
    path('pricing/', views.pricing_view, name='pricing'),
    path('checkout/<uuid:plan_id>/', views.checkout_view, name='checkout'),
]
