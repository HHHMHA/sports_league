from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import BasePermission


class PermissionClassesMixin(UserPassesTestMixin):
    """Allows us to use DRF permission classes"""

    permission_classes: list[BasePermission.__class__] = []
    default_permission_denied_message = _("Permission Denied")

    def test_func(self) -> bool | None:
        for permission_class in self.permission_classes:
            permission = permission_class()
            if not permission.has_permission(self.request, self):
                # Manipulate the message before we raise the error
                self.permission_denied_message = getattr(permission, "message", self.default_permission_denied_message)
                return False
        return True


class IsAnonymous(BasePermission):
    """
    Allows access only to anonymous users
    """

    message = _("You must logout to see this page")

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_anonymous)


class UserInSession(BasePermission):
    message = _("Please follow correct flow")

    def has_permission(self, request, view):
        return "user" in request.session
