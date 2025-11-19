from django.urls import path

from homes.views import PropertyAPIView, PropertyDetailAPIView, PropertyOwnerAPIView, PropertyFeedbackAPIView, \
    PropertyOwnerFeedbackAPIView

urlpatterns = [
    path('properties/', PropertyAPIView.as_view(), name='properties'),
    path('property/<uuid>', PropertyDetailAPIView.as_view(), name='property_detail'),
    path('uploader-properties/', PropertyOwnerAPIView.as_view(), name='property_detail'),
    path('property-feedbacks/', PropertyFeedbackAPIView.as_view(), name='property_feedbacks'),
    path('property-owner-feedbacks/', PropertyOwnerFeedbackAPIView.as_view(), name='property_owner_feedbacks'),
]
