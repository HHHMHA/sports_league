import pytest

from ..notification_types import UserVerificationNotification


@pytest.mark.django_db
class TestUserVerificationNotification:
    def test_get_email(self, user, verification_notification):
        assert verification_notification.get_email() == user.email

    def test_get_context(self, user, verification_notification):
        ctx = verification_notification.get_context()
        assert ctx["code"] == verification_notification.instance.code

    def test_email_slug(self):
        assert UserVerificationNotification.email_slug == "verify_user_sms_email"
