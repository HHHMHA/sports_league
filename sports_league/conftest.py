import pytest
from mixer.backend.django import mixer

from sports_league.common.models import EmailTemplate
from sports_league.users.models import User, UserVerification
from sports_league.users.notification_types import UserVerificationNotification
from sports_league.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture
def email_template(db) -> EmailTemplate:
    # Clear templates made by migrations
    EmailTemplate.objects.all().delete()
    return mixer.blend(EmailTemplate, code="verify_user_sms_email", template=r"Your code is {{ code }}")


@pytest.fixture
def verification_notification(db, user) -> UserVerificationNotification:
    verification = UserVerification.generate_code(user)
    instance = UserVerificationNotification(verification, None)
    return instance
