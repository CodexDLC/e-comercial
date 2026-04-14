from typing import Any, cast

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, UserCreationForm
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy


class AuthModeContextMixin:
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        # Mixins for Django views often trigger 'undefined in superclass' in Mypy
        context = super().get_context_data(**kwargs)  # type: ignore[misc]
        context.update(
            {
                "auth_mode": getattr(settings, "CODEX_AUTH_MODE", "django"),
                "auth_provider": getattr(settings, "CODEX_AUTH_PROVIDER", "django"),
                "allauth_enabled": bool(getattr(settings, "CODEX_ALLAUTH_ENABLED", False)),
            }
        )
        return cast(dict[str, Any], context)


class BrandedLoginView(AuthModeContextMixin, LoginView):
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True

    def is_register_action(self) -> bool:
        return self.request.GET.get("action") == "register"

    def get_template_names(self) -> list[str]:
        if self.is_register_action():
            return ["account/signup.html"]
        return ["account/login.html"]

    def get_form_class(self) -> Any:
        if self.is_register_action():
            return UserCreationForm
        return self.authentication_form

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        if self.is_register_action():
            # UserCreationForm doesn't accept 'request' as a positional or keyword argument
            kwargs.pop("request", None)
        return kwargs

    def form_valid(self, form: AuthenticationForm | UserCreationForm[Any]) -> Any:
        if not self.is_register_action():
            return super().form_valid(cast(AuthenticationForm, form))

        user = cast(UserCreationForm[Any], form).save()
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        return HttpResponseRedirect(self.get_success_url())


class BrandedLogoutView(AuthModeContextMixin, LogoutView):
    http_method_names = ("get", "post", "options")
    template_name = "account/logout.html"


class BrandedPasswordResetView(AuthModeContextMixin, PasswordResetView):
    template_name = "account/password_reset.html"
    email_template_name = "registration/password_reset_email.html"
    form_class = PasswordResetForm
    success_url = reverse_lazy("cabinet:account_reset_password_done")


class BrandedPasswordResetDoneView(AuthModeContextMixin, PasswordResetDoneView):
    template_name = "account/password_reset_done.html"


class BrandedPasswordResetConfirmView(AuthModeContextMixin, PasswordResetConfirmView):
    template_name = "account/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")


class BrandedPasswordResetCompleteView(AuthModeContextMixin, PasswordResetCompleteView):
    template_name = "account/password_reset_complete.html"
