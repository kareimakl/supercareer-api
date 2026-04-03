from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import CV, Proposal
from .serializers import CVSerializer, ProposalSerializer

class CVCreateView(generics.CreateAPIView):
    queryset = CV.objects.all()
    serializer_class = CVSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProposalHistoryView(generics.ListAPIView):
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Proposal.objects.filter(user=self.request.user).order_by('-created_at')

class ProposalDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Proposal.objects.filter(user=self.request.user)
