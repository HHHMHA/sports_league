import string
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField, EmailField
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from .managers import UserManager
from .notifications import UserVerificationNotifier


class User(AbstractUser):
    """
    Default custom user model for sports-league.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def pending_otp(self) -> bool:
        return (
            self.is_active is False
            and UserVerification.objects.filter(
                is_verified=False,
                user=self,
            ).exists()
        )


class UserVerification(TimeStampedModel):
    DELAY_BETWEEN_RESEND = timedelta(seconds=60)  # For resending
    CODE_LENGTH = 6

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="verification")
    code = models.CharField(max_length=CODE_LENGTH)
    is_verified = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "User Verification (OTP Code)"
        verbose_name_plural = "User Verifications (OTP Codes)"

    @staticmethod
    def get_random_number() -> str:
        """generate 6 digit random number"""

        return get_random_string(length=UserVerification.CODE_LENGTH, allowed_chars=string.digits)

    @classmethod
    def generate_code(cls, user):
        """
        generate verification code for given user and mark as pending otp
        """

        user.is_active = False
        user.save()
        obj, is_updated = cls.objects.update_or_create(
            user=user,
            defaults={
                "code": cls.get_random_number(),
                "is_verified": False,
            },
        )
        obj.notifier.send_verification_code_notification(None)
        return obj

    @property
    def notifier(self):
        """
        :return: Notifier instance for this model
        """

        return UserVerificationNotifier(self, [UserVerificationNotifier.EMAIL])

    def set_verified(self):
        """
        Verify and activate the user
        """

        user = self.user
        user.is_active = True
        user.save()
        self.is_verified = True
        self.save()

    @classmethod
    def verify_user(cls, user, code) -> bool:
        try:
            obj = cls.objects.get(user=user, code=code)
            obj.set_verified()
            return True
        except cls.DoesNotExist:
            return False

    @property
    def can_resend(self):
        return (now() - self.modified) >= self.DELAY_BETWEEN_RESEND

    @classmethod
    def check_code(cls, user, code):
        try:
            cls.objects.get(user=user, code=code)
            return True
        except cls.DoesNotExist:
            return False
