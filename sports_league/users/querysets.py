from django.db.models import QuerySet


class UserQuerySet(QuerySet):
    def active(self) -> "UserQuerySet":
        return self.filter(
            is_active=True,
        )

    def pending_otp(self) -> "UserQuerySet":
        return self.filter(
            is_active=False,
            verification__isnull=False,
            verification__is_verified=False,
        )
