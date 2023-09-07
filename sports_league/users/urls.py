from django.urls import path

from .views import RegisterUserView, ResetPasswordView, VerifyUserView

app_name = "users"

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("verification/", VerifyUserView.as_view(), name="verification"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
]
