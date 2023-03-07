from django.shortcuts import render
from rest_framework import generics, status, views, permissions
from .serializers import UserRegisterSerializer, EmailVerificationSerializer, LoginSerializer, UserRegisterWithoutVerificationSerializer
# from .serializers import UserRegisterSerializer, SetNewPasswordSerializer, ResetPasswordEmailRequestSerializer, EmailVerificationSerializer, LoginSerializer, LogoutSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi 
from .renderers import UserRenderer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken






class UserRegisterView(generics.GenericAPIView):

    serializer_class = UserRegisterSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # -----------------------------------
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain
        relativeLink = reverse('email-verify')
        absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
        email_body = 'Hi '+user.username + \
            ' Use the link below to verify your email \n' + absurl
        data = {'email_body': email_body, 'to_email': user.email,'email_subject': 'Verify your email'}

        Util.send_email(data)
        return Response(user_data, status=status.HTTP_201_CREATED)
    

class UserRegisterWithoutVerificationView(generics.CreateAPIView):
    """View for user registration without verification email"""

    serializer_class = UserRegisterWithoutVerificationSerializer
    permission_classes = [AllowAny]


class VerifyEmailView(generics.GenericAPIView):
    """View for verifying user's email address"""

    permission_classes = [AllowAny]

    def get(self, request):
        # try:
        #     user_id = AccessToken(token).payload['user_id']
        #     user = User.objects.get(id=user_id)
        #     user.is_active = True
        #     user.is_verified = True
        #     user.save()
        #     return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        # except jwt.ExpiredSignatureError as identifier:
        #     return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        # except jwt.exceptions.DecodeError as identifier:
        #     return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            # if not user.is_verified:
            user.is_active = True
            user.is_verified = True
            user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        


# class VerifyEmail(views.APIView):
#     serializer_class = EmailVerificationSerializer

#     token_param_config = openapi.Parameter(
#         'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

#     @swagger_auto_schema(manual_parameters=[token_param_config])
#     def get(self, request):
#         token = request.GET.get('token')
#         try:
#             payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
#             user = User.objects.get(id=payload['user_id'])
#             if not user.is_verified:
#                 user.is_verified = True
#                 user.save()
#             return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
#         except jwt.ExpiredSignatureError as identifier:
#             return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
#         except jwt.exceptions.DecodeError as identifier:
#             return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)