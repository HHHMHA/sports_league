from sports_league.common.notifications import BaseNotifier

from .notification_types import UserVerificationNotification


class UserVerificationNotifier(BaseNotifier):
    def init(self, instance, options):
        super().__init__(instance, options)

    def send_verification_code_notification(self, request, **extra_context):
        notification_type = UserVerificationNotification(self.instance, request, **extra_context)
        self.dispatch_notification(notification_type)
