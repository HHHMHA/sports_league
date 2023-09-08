import pytest
from django.conf import settings
from django.templatetags.static import static
from mixer.backend.django import mixer
from tablib import Dataset

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


@pytest.fixture
def game_csv():
    base_dir = settings.BASE_DIR
    return open(f"{base_dir}/sports_league{static('test_resources/data.csv')}", "rb")


@pytest.fixture
def game_dataset():
    dataset = Dataset()
    dataset.headers = ["id", "home_team", "home_team_score", "away_team", "away_team_score"]
    dataset.append(["", "Team A", 2, "Team B", 1])
    return dataset
