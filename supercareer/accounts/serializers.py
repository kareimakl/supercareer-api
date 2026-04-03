from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.crypto import get_random_string
from .models import User, UserProfile, Skill


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    role = serializers.CharField(required=False, default='job_seeker')
    full_name = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, min_length=8)
    skills = serializers.ListField(child=serializers.CharField(), required=False)
    hourly_rate = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0.00)
    specialization = serializers.CharField(required=False, allow_blank=True)
    experience = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    education = serializers.CharField(required=False, allow_blank=True)
    preferences = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'full_name',
                  'skills', 'hourly_rate', 'specialization', 
                  'experience', 'bio', 'education', 'preferences']

    def create(self, validated_data):
        # Extract full_name and split it
        full_name = validated_data.pop('full_name', '')
        if full_name:
            parts = full_name.split(' ', 1)
            validated_data['first_name'] = parts[0] if len(parts) > 0 else ''
            validated_data['last_name'] = parts[1] if len(parts) > 1 else ''
            
        # Handle missing username
        if not validated_data.get('username'):
            email = validated_data.get('email', '')
            base = email.split('@')[0] if email else 'user'
            validated_data['username'] = f"{base}_{get_random_string(6)}"
            
        # Handle missing role
        if not validated_data.get('role'):
            validated_data['role'] = 'job_seeker'
        
        # Extract profile data
        skills_data = validated_data.pop('skills', [])
        profile_fields = ['hourly_rate', 'specialization', 
                          'experience', 'bio', 'education', 'preferences']
        profile_data = {field: validated_data.pop(field) for field in profile_fields if field in validated_data}
        
        # Create user
        user = User.objects.create_user(**validated_data)
        
        # Create profile
        profile = UserProfile.objects.create(user=user, **profile_data)
        
        # Handle skills
        for skill_name in skills_data:
            skill, _ = Skill.objects.get_or_create(name=skill_name.strip())
            profile.skills.add(skill)
        
        return user


class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    username = serializers.CharField(source='user.username', read_only=True)
    
    skills = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'first_name', 'last_name', 'email', 'username', 
                  'bio', 'specialization', 'experience', 'hourly_rate', 
                  'education', 'preferences', 'skills', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['skills'] = [skill.name for skill in instance.skills.all()]
        return rep

    def update(self, instance, validated_data):
        # Handle User model fields
        user_data = validated_data.pop('user', {})
        user = instance.user
        if 'email' in user_data:
            new_email = user_data['email']
            if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                raise serializers.ValidationError({"email": "This email is already in use."})
            user.email = new_email
            
        for attr, value in user_data.items():
            if attr != 'email': # handled separately
                setattr(user, attr, value)
        user.save()

        # Handle skills separately if provided as strings/slugs
        skills_data = validated_data.pop('skills', None)
        if skills_data is not None:
            instance.skills.clear()
            for skill_name in skills_data:
                skill, _ = Skill.objects.get_or_create(name=skill_name.strip())
                instance.skills.add(skill)

        # Handle other profile fields
        return super().update(instance, validated_data)



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        print(f"DEBUG: Serializer .validate() started. Email: {email}")
        
        if email and password:
            attrs[self.username_field] = email
            print(f"DEBUG: Mapped {email} to username_field")
        
        try:
            # Parent validate will handle authentication using the username_field
            data = super().validate(attrs)
            print(f"DEBUG: SimpleJWT validation successful for: {email}")
            
            # WRAP TOKENS FOR FRONTEND CONSISTENCY (Expected by auth.ts)
            tokens = {
                'refresh': data.pop('refresh'),
                'access': data.pop('access'),
            }
            data['tokens'] = tokens
            
            # Add user data to the response
            user_serializer = UserSerializer(self.user)
            data['user'] = user_serializer.data
            
            # Add profile data to the response
            try:
                profile = UserProfile.objects.get(user=self.user)
                profile_serializer = ProfileSerializer(profile)
                data['profile'] = profile_serializer.data
                print(f"DEBUG: Profile data added for: {email}")
            except UserProfile.DoesNotExist:
                data['profile'] = None
                print(f"DEBUG: Profile NOT found for: {email}")
                
            return data
        except Exception as e:
            print(f"DEBUG: SimpleJWT validation failed. Error: {str(e)}")
            raise e

class DashboardStatsSerializer(serializers.Serializer):
    matches_today = serializers.IntegerField()
    active_proposals = serializers.IntegerField()
    avg_match_score = serializers.FloatField()
    profile_views = serializers.IntegerField()
    user_name = serializers.CharField()

class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=True, help_text="Google OAuth2 ID Token")
    role = serializers.CharField(required=False, help_text="Required for registration")

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)
