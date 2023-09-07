import pytest
from django.urls import reverse
from rest_framework import status

from ..models import User, UserVerification


@pytest.mark.django_db
class TestUserViews:
    def test_register_view(self, client):
        url = reverse("users:register")
        data = {
            "email": "test@example.com",
        }
        response = client.post(url, data)
        assert status.is_redirect(response.status_code)
        user_id = client.session["user"]
        assert user_id is not None

        user = User.objects.get(pk=user_id)
        assert user.email == data["email"]
        assert user.pending_otp() is True

    def test_verify_view(self, client, user):
        verification = UserVerification.generate_code(user)
        # To modify the session and then save it, it must be stored in a variable first
        # (because a new SessionStore is created every time this property is accessed)
        session = client.session
        session["user"] = user.pk
        session.save()
        url = reverse("users:verification")
        data = {
            "password1": "P@assWord",
            "password2": "P@assWord",
            "code": verification.code,
        }

        response = client.post(url, data)
        assert status.is_redirect(response.status_code)

        user.refresh_from_db()
        assert user.pending_otp() is False
        assert user.check_password("P@assWord") is True

    def test_verify_view__requires_session(self, client, user):
        verification = UserVerification.generate_code(user)

        url = reverse("users:verification")
        data = {
            "password1": "P@assWord",
            "password2": "P@assWord",
            "code": verification.code,
        }

        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_verify_view__requires_correct_code(self, client, user):
        UserVerification.generate_code(user)
        # To modify the session and then save it, it must be stored in a variable first
        # (because a new SessionStore is created every time this property is accessed)
        session = client.session
        session["user"] = user.pk
        session.save()
        url = reverse("users:verification")
        data = {
            "password1": "P@assWord",
            "password2": "P@assWord",
            "code": "whattt",
        }

        response = client.post(url, data)
        assert status.is_success(response.status_code)
        assert "code" in response.context["form"].errors

        user.refresh_from_db()
        assert user.pending_otp() is True
        assert user.check_password("P@assWord") is False

    def test_reset_view(self, client, user):
        url = reverse("users:reset_password")
        data = {
            "email": user.email,
        }
        response = client.post(url, data)
        assert status.is_redirect(response.status_code)
        user_id = client.session["user"]
        assert user_id is not None

        user = User.objects.get(pk=user_id)
        assert user.email == data["email"]
        assert user.pending_otp() is True

    def test_reset_view__no_email(self, client):
        url = reverse("users:reset_password")
        data = {
            "email": "test@example.com",
        }
        response = client.post(url, data)
        assert status.is_success(response.status_code)
        assert "email" in response.context["form"].errors
