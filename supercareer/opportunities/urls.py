from django.urls import path
from .views import JobListView, ProjectListView, ProposalCreateView, RefreshProjectsView

urlpatterns = [
    path('jobs/', JobListView.as_view(), name='job-list'),
    path('projects/', ProjectListView.as_view(), name='project-list'),
    path('projects/refresh/', RefreshProjectsView.as_view(), name='project-refresh'),
    path('proposals/create/', ProposalCreateView.as_view(), name='proposal-create'),
]
