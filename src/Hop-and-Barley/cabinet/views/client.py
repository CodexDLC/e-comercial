from typing import Any

from django.contrib import messages
from django.views.generic import TemplateView

from cabinet.services.client import ClientService


class ClientHomeView(TemplateView):
    template_name = "cabinet/client/corner.html"

    def dispatch(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        request.cabinet_space = "client"
        request.cabinet_module = "client"
        return super().dispatch(request, *args, **kwargs)

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        success, message = ClientService.save_corner_profile(request)
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(ClientService.get_corner_context(self.request))
        return context


class ClientAppointmentsView(TemplateView):
    template_name = "cabinet/client/appointments.html"

    def dispatch(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        request.cabinet_space = "client"
        request.cabinet_module = "client"
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(ClientService.get_appointments_context(self.request))
        return context
