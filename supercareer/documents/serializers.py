from rest_framework import serializers
from .models import CV, Proposal
from opportunities.serializers import JobSerializer, ProjectSerializer

class CVSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV
        fields = '__all__'

class ProposalSerializer(serializers.ModelSerializer):
    job_details = JobSerializer(source='job', read_only=True)
    project_details = ProjectSerializer(source='project', read_only=True)

    class Meta:
        model = Proposal
        fields = ['id', 'user', 'job', 'project', 'content', 'status', 'created_at', 'job_details', 'project_details']
        read_only_fields = ['user', 'created_at']
