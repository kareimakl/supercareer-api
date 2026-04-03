from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema
from .models import ScrapingLog, AdminActivity
from .serializers import (
    ScrapingLogSerializer, 
    AdminActivitySerializer, 
    AdminStatsSerializer
)
from accounts.models import User
from opportunities.models import Job, FreelanceProject
from accounts.serializers import UserSerializer

class AdminStatsView(views.APIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminStatsSerializer

    @extend_schema(responses={200: AdminStatsSerializer})
    def get(self, request):
        stats = {
            "total_users": User.objects.count(),
            "total_jobs": Job.objects.count(),
            "total_projects": FreelanceProject.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "blocked_users": getattr(User, 'is_blocked', False) and User.objects.filter(is_blocked=True).count() or 0,
        }
        return Response(stats)

class ScrapingLogListView(generics.ListAPIView):
    queryset = ScrapingLog.objects.all().order_by('-created_at')
    serializer_class = ScrapingLogSerializer
    permission_classes = [IsAdminUser]

class AdminActivityListView(generics.ListAPIView):
    queryset = AdminActivity.objects.all().order_by('-created_at')
    serializer_class = AdminActivitySerializer
    permission_classes = [IsAdminUser]

class UserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

class UserBlockToggleView(views.APIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer # generic placeholder or specialized

    @extend_schema(responses={200: UserSerializer})
    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            # Check if is_blocked exists, otherwise use is_active toggle
            if hasattr(user, 'is_blocked'):
                user.is_blocked = not user.is_blocked
            else:
                user.is_active = not user.is_active
            user.save()
            
            # Log the action
            AdminActivity.objects.create(
                admin=request.user,
                action=f"Toggled block/active status for user {user.email}",
                target_user=user
            )
            
            return Response({"status": "Status toggled successfully", "is_active": user.is_active})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
