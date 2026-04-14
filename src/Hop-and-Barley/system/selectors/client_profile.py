from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser

from system.models import UserProfile

User = get_user_model()


class ClientProfileSelector:
    @staticmethod
    def get_or_create_profile(user: AbstractBaseUser | AnonymousUser) -> UserProfile:
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "source": "manual",
            },
        )
        return profile
