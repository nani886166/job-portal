from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
import random
import string
import threading
from rest_framework import serializers
from django.contrib.auth import get_user_model
import random
from django.core.mail import send_mail
from django.conf import settings
import dns.resolver
from django.core.cache import cache
        

User = get_user_model()
import dns.resolver

def is_real_email_domain(email):
    domain = email.split('@')[-1]
    try:
        dns.resolver.resolve(domain, 'MX')
        return True
    except:
        return False
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'password', 'confirm_password')

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user
    def validate_email(self, value):
        if not is_real_email_domain(value):
            raise serializers.ValidationError("Please use a valid email address (real domain).")
        return value 

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
            }
        }
User = get_user_model()
def send_email_async(subject, message, recipient_list):
    def _send():
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
    thread = threading.Thread(target=_send)
    thread.start()

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user with this email address.")
        return value

    def save(self):
        email = self.validated_data['email']
        otp = ''.join(random.choices(string.digits, k=6))
        cache.set(f'reset_otp_{email}', otp, timeout=600)   # store OTP for 10 min

        # Send real email (no terminal)
        send_email_async(
            subject='Password Reset OTP',
            message=f'Your OTP for password reset is: {otp}',
            recipient_list=[email],
        )
        return otp   # still return for potential dev use, but not to frontend

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, required=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({"confirm_new_password": "Passwords do not match."})
        return attrs

    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)   # This is CRITICAL
            user.save()
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
