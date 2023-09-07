from django.urls import reverse_lazy
from django.views.generic import CreateView

from ..common.permissions import IsAnonymous, PermissionClassesMixin, UserInSession
from .forms import RegisterUserForm, ResetPasswordForm, UserVerificationForm
from .models import User


class RegisterUserView(PermissionClassesMixin, CreateView):
    template_name = "registration/register.html"
    form_class = RegisterUserForm
    success_url = reverse_lazy("users:verification")
    permission_classes = [IsAnonymous]
    raise_exception = True

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session["user"] = self.object.pk
        return response


class VerifyUserView(PermissionClassesMixin, CreateView):
    template_name = "registration/verification.html"
    form_class = UserVerificationForm
    success_url = reverse_lazy("login")
    permission_classes = [IsAnonymous, UserInSession]
    raise_exception = True

    def get_form_kwargs(self):
        ctx = super().get_form_kwargs()
        ctx["user"] = User.objects.get(pk=self.request.session["user"])
        return ctx


class ResetPasswordView(RegisterUserView):
    template_name = "registration/reset_password.html"
    form_class = ResetPasswordForm
