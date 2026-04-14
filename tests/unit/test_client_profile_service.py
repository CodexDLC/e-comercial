import pytest
from django.contrib.auth import get_user_model

from system.services.client_profile import ClientProfilePayload, ClientProfileService

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestClientProfileService:
    def test_parse_form_data_success(self):
        form_data = {
            "first_name": " John ",
            "last_name": "Doe",
            "email": "john@example.com",
            "birth_date": "1990-01-01",
        }
        clean_data, error = ClientProfileService.parse_form_data(form_data)
        assert error is None
        assert clean_data["first_name"] == "John"
        assert clean_data["birth_date"] == "1990-01-01"

    def test_parse_form_data_invalid_date(self):
        form_data = {"birth_date": "invalid-date"}
        clean_data, error = ClientProfileService.parse_form_data(form_data)
        assert error is not None
        assert clean_data == {}

    def test_save_profile_success(self, user):
        payload = ClientProfilePayload(
            first_name="Jane",
            last_name="Smith",
            patronymic="Ivanovna",
            phone="+79991234567",
            email="jane@example.com",
            birth_date="1995-05-05",
        )
        success, message = ClientProfileService.save_profile(user, payload)
        assert success is True

        user.refresh_from_db()
        profile = user.profile  # Assuming related_name='profile' or similar
        assert user.first_name == "Jane"
        assert profile.phone == "+79991234567"
        assert profile.birth_date.isoformat() == "1995-05-05"
