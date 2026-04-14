from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.utils.translation import gettext_lazy as _

from system.models import UserProfile
from system.selectors.client_profile import ClientProfileSelector

User = get_user_model()


@dataclass(frozen=True)
class ClientProfilePayload:
    first_name: str
    last_name: str
    patronymic: str
    phone: str
    email: str
    birth_date: str


class ClientProfileService:
    @staticmethod
    def get_profile_payload(user: AbstractBaseUser | AnonymousUser) -> tuple[UserProfile, ClientProfilePayload]:
        profile = ClientProfileSelector.get_or_create_profile(user)
        payload = ClientProfilePayload(
            first_name=profile.first_name or user.first_name or "",
            last_name=profile.last_name or user.last_name or "",
            patronymic=profile.patronymic or "",
            phone=profile.phone or "",
            email=user.email or "",
            birth_date=profile.birth_date.isoformat() if profile.birth_date else "",
        )
        return profile, payload

    @staticmethod
    def parse_form_data(form_data: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
        """Parses and validates form data for client profile."""
        clean_data = {
            "first_name": form_data.get("first_name", "").strip(),
            "last_name": form_data.get("last_name", "").strip(),
            "email": form_data.get("email", "").strip(),
            "patronymic": form_data.get("patronymic", "").strip(),
            "phone": form_data.get("phone", "").strip(),
        }

        raw_birth_date = form_data.get("birth_date", "").strip()
        if raw_birth_date:
            try:
                datetime.strptime(raw_birth_date, "%Y-%m-%d").date()
                clean_data["birth_date"] = raw_birth_date
            except ValueError:
                return {}, str(_("Date of birth must use the YYYY-MM-DD format."))
        else:
            clean_data["birth_date"] = ""

        return clean_data, None

    @staticmethod
    def save_profile(user: AbstractBaseUser, payload: ClientProfilePayload) -> tuple[bool, str]:
        """Saves profile data from payload."""
        profile = ClientProfileSelector.get_or_create_profile(user)

        user.first_name = payload.first_name
        user.last_name = payload.last_name
        user.email = payload.email

        profile.first_name = payload.first_name
        profile.last_name = payload.last_name
        profile.patronymic = payload.patronymic
        profile.phone = payload.phone
        profile.birth_date = datetime.strptime(payload.birth_date, "%Y-%m-%d").date() if payload.birth_date else None

        user.save(update_fields=["first_name", "last_name", "email"])
        profile.save(update_fields=["first_name", "last_name", "patronymic", "phone", "birth_date"])
        return True, str(_("Profile updated successfully."))
