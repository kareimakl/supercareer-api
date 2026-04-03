from django.urls import path
from .views import (
    AdminStatsView, 
    ScrapingLogListView, 
    AdminActivityListView, 
    UserListView,
    UserBlockToggleView
)

urlpatterns = [
    path('stats/', AdminStatsView.as_view(), name='admin-stats'),
    path('scraping-logs/', ScrapingLogListView.as_view(), name='scraping-logs'),
    path('activities/', AdminActivityListView.as_view(), name='admin-activities'),
    path('users/', UserListView.as_view(), name='admin-users'),
    path('users/<int:pk>/toggle-block/', UserBlockToggleView.as_view(), name='admin-user-block-toggle'),
]
