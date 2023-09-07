from django import forms
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.forms import EmailField
from django.utils.translation import gettext_lazy as _

from .models import UserVerification

User = get_user_model()


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User
        field_classes = {"email": EmailField}


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        fields = ("email",)
        field_classes = {"email": EmailField}
        error_messages = {
            "email": {"unique": _("This email has already been taken.")},
        }


class RegisterUserForm(forms.ModelForm):
    password1 = None
    password2 = None

    class Meta:
        model = User
        fields = ("email",)

    def save(self, commit: bool = True) -> User:
        instance = super().save(commit=commit)
        if commit:
            UserVerification.generate_code(instance)
        return instance


class UserVerificationForm(forms.Form):
    def __init__(self, user, **kwargs):
        kwargs.pop("instance")
        super().__init__(**kwargs)
        self.user = user

    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
        "code_incorrect": _("The entered code is incorrect."),
    }
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )
    code = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
            )
        return password2

    def clean_code(self):
        code = self.cleaned_data["code"]
        if not UserVerification.check_code(self.user, code):
            raise ValidationError(
                self.error_messages["code_incorrect"],
            )
        return code

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        code = cleaned_data.pop("code")
        self.user.set_password(cleaned_data["password1"])
        if commit:
            self.user.save()
            UserVerification.verify_user(self.user, code)
        return self.user


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(label=_("Email Address"))

    def __init__(self, **kwargs):
        kwargs.pop("instance")
        super().__init__(**kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"]
        user = User.objects.filter(email=email).first()
        self.cleaned_data["user"] = user
        if not user:
            raise ValidationError(_("No email address was found"))
        return email

    class Meta:
        model = User
        fields = ("email",)

    def save(self, commit=True):
        instance = self.cleaned_data["user"]
        if commit:
            UserVerification.generate_code(instance)
        return instance
