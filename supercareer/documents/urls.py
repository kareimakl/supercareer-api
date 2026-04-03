from django.urls import path
from .views import CVCreateView, ProposalHistoryView, ProposalDetailView

urlpatterns = [
    path('cv/create/', CVCreateView.as_view(), name='cv-create'),
    path('proposals/', ProposalHistoryView.as_view(), name='proposal-history'),
    path('proposals/<int:pk>/', ProposalDetailView.as_view(), name='proposal-detail'),
]
