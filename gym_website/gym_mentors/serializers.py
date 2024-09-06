from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from .models import Mentors

class MentorSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Mentors
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone_number', 'expertise', 'admin', 'Gym']

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
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError("Username and password are required.")

        try:
            user = Mentors.objects.get(username=username)
        except Mentors.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")

        # Use check_password to verify the hashed password
        if not check_password(password, user.password):
            raise serializers.ValidationError("Invalid credentials.")

        data['user'] = user
        return data
