from rest_framework import serializers
from .models import CustomUserRegistration
from django.contrib.auth import authenticate
from gym_details.models import GymDetails

class UserRegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(max_length=20, write_only=True, required=False)
    password2 = serializers.CharField(max_length=20, write_only=True, required=False)

    class Meta:
        model = CustomUserRegistration
        fields = ('id', 'username', 'first_name', 'last_name', 'password1', 'password2', 'email', 'phone_number', 'country')

    def validate(self, attrs):
        if 'password1' in attrs and 'password2' in attrs:
            if attrs['password1'] != attrs['password2']:
                raise serializers.ValidationError({"password": "Password and confirm password do not match."})
        return attrs

    def create(self, validated_data):
        if 'password1' in validated_data and 'password2' in validated_data:
            validated_data.pop('password2')
            user = CustomUserRegistration.objects.create_user(
                username=validated_data.get('username', ''),
                password=validated_data.get('password1', ''),
                email=validated_data.get('email', ''),
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
                phone_number=validated_data.get('phone_number', ''),
                country=validated_data.get('country', '')
            )
            return user 
    def update(self, instance, validated_data):
        if 'password1' in validated_data and 'password2' in validated_data:
            if validated_data['password1'] != validated_data['password2']:
                raise serializers.ValidationError({"password": "Passwords do not match"})
            else:
                instance.set_password(validated_data['password1'])
    
        for key, value in validated_data.items():
            if key not in ['password1', 'password2']:
                setattr(instance, key, value)
        instance.save()
        return instance

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs['username']
        password = attrs['password']

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid username and password")
        else:
            raise serializers.ValidationError("Both username and password are required")
        
        attrs['user'] = user
        return attrs

class AdminRegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(max_length=20, write_only=True)
    password2 = serializers.CharField(max_length=20, write_only=True)

    class Meta:
        model = CustomUserRegistration
        fields = ('id','username', 'first_name', 'last_name', 'password1', 'password2', 'email', 'gym_name', 'gym_address', 'gym_phone_number', 'country', 'phone_number')

    def validate(self, attrs):
        required_fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'email', 'gym_name', 'gym_address', 'gym_phone_number', 'country', 'phone_number']
        missing_fields = [field for field in required_fields if field not in attrs or attrs[field] == '']

        if missing_fields:
            raise serializers.ValidationError({field: "This field is required." for field in missing_fields})
        
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password and confirm password do not match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUserRegistration.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password1'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            gym_name=validated_data['gym_name'],
            gym_address=validated_data['gym_address'],
            gym_phone_number=validated_data['gym_phone_number'],
            country=validated_data['country'],
            phone_number=validated_data['phone_number'],
            is_staff=True,
            is_active=True
        )
        return user
    
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            if key == 'password1' and 'password2' in validated_data:
                if validated_data['password1'] != validated_data['password2']:
                    raise serializers.ValidationError({"password": "Passwords do not match"})
                else:
                    instance.set_password(validated_data['password1'])
            elif key in ['username', 'first_name', 'last_name', 'email', 'phone_number', 'country', 'gym_name', 'gym_address', 'gym_phone_number']:
                setattr(instance, key, value)
        
        instance.save()
        return instance


class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs['username']
        password = attrs['password']

        if username and password:
            user = authenticate(username=username, password=password)
            if not user or not user.is_staff:
                raise serializers.ValidationError("Invalid username and password or not an admin user")
        else:
            raise serializers.ValidationError("Both username and password are required")
        
        attrs['user'] = user
        return attrs
    
class SuperUserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs['username']
        password = attrs['password']

        if username and password:
            user = authenticate(username=username, password=password)
            if not user or not user.is_staff or not user.is_superuser:
                raise serializers.ValidationError("Unauthorized Access")
        else:
            raise serializers.ValidationError("Both username and password are required")
        
        attrs['user'] = user
        return attrs
    
class PasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)