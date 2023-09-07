import pytest
from django.template.loader import render_to_string

from sports_league.common.models import EmailTemplate
from sports_league.users.notification_types import UserVerificationNotification


@pytest.mark.django_db
class TestEmailTemplate:
    def test_verification_template__exists(self):
        assert EmailTemplate.objects.filter(code=UserVerificationNotification.email_slug).exists() is True

    def test_get_or_render__when_exists(self, email_template: EmailTemplate):
        subject, body = EmailTemplate.get_or_render(code=email_template.code, context={"code": "123456"})
        assert body == "Your code is 123456"

    def test_get_or_render__when_not_exists(self):
        with pytest.raises(EmailTemplate.DoesNotExist):
            EmailTemplate.get_or_render(code="something", context={"code": "123456"})

    def test_get_or_render__when_external_template(self):
        # we can mock this instead
        subject, body = EmailTemplate.get_or_render(code="test", template="404.html", context={"code": "123456"})
        assert body == render_to_string("404.html")
