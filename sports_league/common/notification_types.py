from django.utils.translation import get_language


class BaseNotificationType:
    sms_slug = None
    email_slug = None
    push_slug = None

    def __init__(self, instance, request, **extra_context):
        self.instance = instance
        self.request = request
        self.extra_context = extra_context
        language = get_language()
        self.language = extra_context.get("language", language)

    def get_email(self):
        raise NotImplementedError()

    def get_device(self):
        raise NotImplementedError()

    def get_number(self):
        raise NotImplementedError()

    def get_context(self) -> dict:
        """
        serve as context for template
        & serve as payload for push notification
        """
        context = self.extra_context.copy()
        return context
