from django.urls import path
from rest_framework.routers import DefaultRouter

from homes.views import PropertyAPIView, PropertyDetailAPIView, PropertyOwnerAPIView

urlpatterns = [
    path('properties/', PropertyAPIView.as_view(), name='properties'),
    path('property/<uuid>', PropertyDetailAPIView.as_view(), name='property_detail'),
    path('uploader-properties/', PropertyOwnerAPIView.as_view(), name='property_detail'),
]
