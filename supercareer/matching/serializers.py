from rest_framework import serializers
from .models import MatchResult
from opportunities.serializers import JobSerializer, ProjectSerializer

class MatchResultSerializer(serializers.ModelSerializer):
    job_details = JobSerializer(source='job', read_only=True)
    project_details = ProjectSerializer(source='project', read_only=True)
    
    class Meta:
        model = MatchResult
        fields = ['id', 'user', 'job', 'project', 'match_score', 'created_at', 
                  'job_details', 'project_details', 'matched_skills', 'missing_skills', 'ai_tips']
