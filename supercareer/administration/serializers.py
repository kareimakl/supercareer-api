from rest_framework import serializers
from .models import ScrapingLog, AdminActivity
from accounts.models import User

class ScrapingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapingLog
        fields = '__all__'

class AdminActivitySerializer(serializers.ModelSerializer):
    admin_name = serializers.CharField(source='admin.username', read_only=True)
    target_user_name = serializers.CharField(source='target_user.username', read_only=True)

    class Meta:
        model = AdminActivity
        fields = ['id', 'admin', 'admin_name', 'action', 'target_user', 'target_user_name', 'created_at']

class AdminStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_jobs = serializers.IntegerField()
    total_projects = serializers.IntegerField()
    active_users = serializers.IntegerField()
    blocked_users = serializers.IntegerField()
