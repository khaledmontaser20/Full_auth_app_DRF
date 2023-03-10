
from rest_framework import serializers
from .models import User
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils import timezone
from .validators import validate_password
# import re



class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, validators=[validate_password])

    default_error_messages = {
        'username': 'The username should only contain alphanumeric characters'}

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'confirm_password']

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        

        if password != confirm_password:
            raise serializers.ValidationError("The passwords do not match.")

        if not username.isalnum():
            raise serializers.ValidationError(
                self.default_error_messages)
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.is_active = False  
        user.save()
        return user
    


class UserRegisterWithoutVerificationSerializer(UserRegisterSerializer):
    """Serializer for user registration without verification email"""

    def create(self, validated_data):
        user = super().create(validated_data)
        user.is_active = True  # Set user as active
        user.is_verified = True  # Set user as active
        user.save()
        return user
    

# class EmailVerificationSerializer(serializers.ModelSerializer):
#     token = serializers.CharField(max_length=555)

#     class Meta:
#         model = User
#         fields = ['token']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
         
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(
        max_length=255, min_length=3, read_only=True)

    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])

        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }

    class Meta:
        model = User
        fields = ['email', 'password', 'username', 'tokens']
        
    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        # filtered_user_by_email = User.objects.filter(email=email)
        user = auth.authenticate(email=email, password=password)

        # if filtered_user_by_email.exists() and filtered_user_by_email[0].auth_provider != 'email':
        #     raise AuthenticationFailed(
        #         detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')
        user.last_login = timezone.now()
        user.save()

        return {
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens
        }

        return super().validate(attrs)

    # def validate(self, attrs):
    #     email = attrs.get('email', '')
    #     password = attrs.get('password', '')
    #     # filtered_user_by_email = User.objects.filter(email=email)
    #     user = auth.authenticate(email=email, password=password)

    #     # if filtered_user_by_email.exists() and filtered_user_by_email[0].auth_provider != 'email':
    #     #     raise AuthenticationFailed(
    #     #         detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)
    #     if user and user.is_active:
    #         user.last_login = timezone.now()
    #         user.save()

    #         return {
    #             'email': user.email,
    #             'username': user.username,
    #             'tokens': user.tokens
    #         }

    #         return super().validate(attrs)

    #     else:
    #         if not user:
    #             raise AuthenticationFailed('User does not exist')
    #         elif not user.is_active:
    #             raise AuthenticationFailed('Account is disabled contact the admin')
    #         else:
    #             raise AuthenticationFailed('Invalid credentials, try again')
        
    # --------------------------------------------------------------------------------------
    # def validate(self, attrs):
    #     email = attrs.get('email', '')
    #     password = attrs.get('password', '')
    #     user = User.objects.filter(email=email).first()

    #     if user and user.is_active and auth.check_password(password, user.password):
    #         user.last_login = timezone.now()
    #         user.save()
    #         return {
    #             'email': user.email,
    #             'username': user.username,
    #             'tokens': user.tokens
    #         }
    #     else:
    #         if not user:
    #             raise AuthenticationFailed('User does not exist')
    #         elif not user.is_active:
    #             raise AuthenticationFailed('Account is disabled contact the admin')
    #         else:
    #             raise AuthenticationFailed('Invalid credentials, try again')





class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:    
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)
    





class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')





