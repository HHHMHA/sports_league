from django.contrib import admin

from .models import EmailTemplate


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    fields = (
        "code",
        "template",
    )
    list_display = ("code",)
