from django.urls import path
from .views import UserRegisterView, VerifyEmailView, LoginAPIView, UserRegisterWithoutVerificationView


urlpatterns = [
    path('register_with_sending_verification_mail/', UserRegisterView.as_view(), name="register_with_sending_verification_mail"),
    path('register_without_sending_verification_mail/', UserRegisterWithoutVerificationView.as_view(), name="register_without_sending_verification_mail"),
    path('email-verify/', VerifyEmailView.as_view(), name="email-verify"),
    path('login/', LoginAPIView.as_view(), name="login"),
]