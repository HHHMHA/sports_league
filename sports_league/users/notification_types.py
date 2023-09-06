from sports_league.common.notification_types import BaseNotificationType


class UserVerificationNotification(BaseNotificationType):
    sms_slug = "verify_user_sms"
    email_slug = "verify_user_sms_email"
    push_slug = "verify_user_sms_push"

    def __init__(self, instance, request, **extra_context):
        super().__init__(instance, request, **extra_context)

    def get_email(self):
        return self.instance.user.email

    def get_device(self):
        return None

    def get_number(self):
        return None

    def get_context(self):
        context = super().get_context()
        context["code"] = self.instance.code
        return context
