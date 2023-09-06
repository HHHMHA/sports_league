from django.db import models
from django.template import Context, Template
from django.template.loader import render_to_string
from django_extensions.db.models import TimeStampedModel


class EmailTemplate(TimeStampedModel):
    code = models.CharField(max_length=255, unique=True)
    subject = models.CharField(max_length=255, null=False, blank=False)
    template = models.TextField(null=False, blank=True)

    class Meta:
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"

    def __str__(self):
        return self.code

    @classmethod
    def get_or_render(cls, code: str, template: str = None, context: dict = None) -> (str, str):
        """
        :return: a tuple that contains the subject and body of the email
        """

        if context is None:
            context = {}

        email_template = cls.objects.filter(code=code).first()
        if email_template:
            template = Template(email_template.template)
            return email_template.subject, template.render(context=Context(context))

        if not template:
            raise cls.DoesNotExist("%s matching query does not exist." % cls._meta.object_name)

        return "Subject", render_to_string(template, context)
