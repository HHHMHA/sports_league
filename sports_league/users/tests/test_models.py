from datetime import timedelta
from unittest.mock import patch

import pytest

from ..models import UserVerification
from ..notifications import UserVerificationNotifier


@pytest.mark.django_db
class TestUser:
    def test_pending_otp(self, user):
        assert user.pending_otp() is False
        UserVerification.generate_code(user)
        user.refresh_from_db()
        assert user.pending_otp() is True


@pytest.mark.django_db
class TestUserVerification:
    def test_generate_code(self, user):
        with patch.object(UserVerificationNotifier, "send_verification_code_notification") as mock:
            obj = UserVerification.generate_code(user)
            assert obj.code is not None
            assert obj.is_verified is False
            assert user.is_active is False
            mock.assert_called_once()

    def test_set_verified(self, user):
        with patch.object(UserVerificationNotifier, "send_verification_code_notification"):
            obj = UserVerification.generate_code(user)
            obj.set_verified()
            assert obj.user.is_active is True
            assert obj.is_verified is True

    def test_verify_user(self, user):
        with patch.object(UserVerificationNotifier, "send_verification_code_notification"):
            obj = UserVerification.generate_code(user)
            assert UserVerification.verify_user(user, obj.code) is True
            user.refresh_from_db()
            assert user.is_active is True
            obj.refresh_from_db()
            assert obj.is_verified is True

    def test_verify_user__not_found(self, user):
        assert UserVerification.verify_user(user, "123456") is False

    def test_verify_user__otp_wrong(self, user):
        with patch.object(UserVerificationNotifier, "send_verification_code_notification"):
            obj = UserVerification.generate_code(user)
            assert UserVerification.verify_user(user, "test") is False
            user.refresh_from_db()
            assert user.is_active is False
            obj.refresh_from_db()
            assert obj.is_verified is False

    def test_can_resend__false(self, user):
        with patch.object(UserVerificationNotifier, "send_verification_code_notification"):
            obj = UserVerification.generate_code(user)
            assert obj.can_resend is False

    def test_can_resend__true(self, user):
        with patch.object(UserVerificationNotifier, "send_verification_code_notification"):
            obj = UserVerification.generate_code(user)
            UserVerification.DELAY_BETWEEN_RESEND = timedelta(seconds=0)
            assert obj.can_resend is True
