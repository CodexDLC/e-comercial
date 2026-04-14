from typing import Any

from django.http import HttpResponseNotFound
from django.views import View


class BookingSettingsForm:  # pragma: no cover - scaffold fallback
    pass


class _BookingDisabledView(View):
    def dispatch(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseNotFound:
        return HttpResponseNotFound("Booking module is disabled in this scaffold.")


class BaseBookingView(_BookingDisabledView):
    pass


class BookingScheduleView(_BookingDisabledView):
    pass


class NewBookingView(_BookingDisabledView):
    pass


class BookingCreateView(_BookingDisabledView):
    pass


class BookingListView(_BookingDisabledView):
    pass


class BookingModalView(_BookingDisabledView):
    pass


class BookingActionView(_BookingDisabledView):
    pass


class BookingSettingsView(_BookingDisabledView):
    pass
