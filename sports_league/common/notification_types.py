class BaseNotificationType:
    sms_slug = None
    email_slug = None
    push_slug = None
    event_type = ""
    display_event_type = ""
    user = None

    def __init__(self, instance, request, **extra_context):
        self.instance = instance
        self.request = request
        self.extra_context = extra_context
        language = "en"
        if request:
            language = request.LANGUAGE_CODE
        self.language = extra_context.get("language", language)

    def get_email(self):
        raise NotImplementedError()

    def get_device(self):
        raise NotImplementedError()

    def get_number(self):
        raise NotImplementedError()

    def get_context(self):
        """
        serve as context for template
        & serve as payload for push notification
        """
        context = self.extra_context.copy()
        return context
