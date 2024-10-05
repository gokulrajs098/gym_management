from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from .models import Mentors
from user_auth.serializers import AdminRegistrationSerializer
from user_auth.models import CustomUserRegistration

class MentorSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    admin = serializers.PrimaryKeyRelatedField(queryset=CustomUserRegistration.objects.filter(is_staff=True), required=True, write_only=True)

    class Meta:
        model = Mentors
        fields = ['id','username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone_number', 'expertise', 'admin', 'Gym', 'is_login']

    def validate(self, attrs):
        # Check if username already exists
        if Mentors.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({'username': 'Username already exists.'})
        
        # Check if password1 and password2 match
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        
        return attrs

    def create(self, validated_data):
        # Pop password2 if it exists
        validated_data.pop('password2', None)
        
        # Hash the password before saving
        validated_data['password1'] = make_password(validated_data['password1'])
        
        mentor = Mentors.objects.create(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password1'],
            phone_number=validated_data['phone_number'],
            expertise=validated_data['expertise'],
            admin=validated_data['admin'],
            Gym = validated_data['Gym']
        )
        return mentor

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        
        # Update password only if it's provided in the validated_data
        password = validated_data.get('password1', None)
        if password:
            instance.password = make_password(password)
        
        instance.expertise = validated_data.get('expertise', instance.expertise)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()
        return instance


class MentorLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=200)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        try:
            mentor = Mentors.objects.get(username=username)
            if not check_password(password, mentor.password):  # Compare hashed password
                raise serializers.ValidationError("Invalid password.")
        except Mentors.DoesNotExist:
            raise serializers.ValidationError("Mentor not found.")

        attrs['mentor'] = mentor
        return attrs