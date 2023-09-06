from unittest.mock import patch

import pytest
from django.core import mail
from django.test import override_settings

from ...common.notifications import send_email_in_bg
from ..models import UserVerification


@pytest.mark.django_db
class TestUserVerificationNotifier:
    def test_send_verification_code_notification(self, user, email_template):
        # we don't care about the inner logic of how the email was sent only that it was sent
        obj = UserVerification.generate_code(user)
        assert len(mail.outbox) == 1
        assert mail.outbox[0].body == f"Your code is {obj.code}"

    @override_settings(ASYNC_NOTIFICATIONS=True)
    def test_send_verification_code_notification_async(self, user, email_template):
        # we don't care about the inner logic of how the email was sent only that it was sent
        with patch.object(send_email_in_bg, "delay") as mock:
            obj = UserVerification.generate_code(user)
            mock.assert_called_once_with(email_template.code, user.email, {"code": obj.code}, language=None)
