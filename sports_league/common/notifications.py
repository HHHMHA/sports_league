import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django_rq import job

from .models import EmailTemplate
from .notification_types import BaseNotificationType

logger = logging.getLogger(__name__)


class BaseNotifier:
    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"

    def __init__(self, instance, options):
        self.instance = instance
        self.options = options

    def dispatch_notification(self, notification_type: BaseNotificationType):
        if self.SMS in self.options:
            self._dispatch_sms(notification_type)

        if self.EMAIL in self.options:
            self._dispatch_email(notification_type)

        if self.PUSH in self.options:
            self._dispatch_push_notifications(notification_type)

    def _dispatch_sms(self, notification_type):
        # Not needed
        pass

    def _dispatch_email(self, notification_type):
        slug = notification_type.email_slug
        request = notification_type.request
        email = notification_type.get_email()
        language = notification_type.extra_context.get("language")
        context = notification_type.get_context()
        send_email(slug, request, email, language, context)

    def _dispatch_push_notifications(self, notification_type):
        # Not needed
        pass


@job
def send_email_in_bg(slug, recipient, context, language, **kwargs):
    # if we need to use a package for email we can just change this now
    logger.info(f"sending email to {recipient}")

    email_subject, email_body = EmailTemplate.get_or_render(code=slug, context=context)
    send_mail(
        email_subject,
        strip_tags(email_body),
        None,
        [recipient],
        html_message=email_body,
    )
    logger.info(f"email send process completed {recipient}")


def send_email(slug, request, recipient, language, context):
    function = send_email_in_bg
    if settings.ASYNC_NOTIFICATIONS:
        function = send_email_in_bg.delay
    try:
        function(
            slug,
            recipient,
            context,
            language=language,
        )
    except Exception as e:
        logger.error(f"Error while sending email with context {context}")
        logger.error(str(e), stack_info=True, exc_info=True)
