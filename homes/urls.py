from django.urls import path
from rest_framework.routers import DefaultRouter

from homes.views import PropertyAPIView

urlpatterns = [
    path('properties', PropertyAPIView.as_view(), name='properties'),
]
