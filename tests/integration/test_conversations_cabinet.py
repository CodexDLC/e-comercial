import pytest
from django.urls import reverse

from features.conversations.cabinet import _conversations_bell, provide_conversations_stats
from features.conversations.models import Message


@pytest.mark.unit
@pytest.mark.django_db
class TestConversationsCabinet:
    def test_conversations_bell(self, rf):
        # Create unread messages
        Message.objects.create(sender_name="S1", sender_email="s1@ex.co", body="B1", is_read=False)
        Message.objects.create(sender_name="S2", sender_email="s2@ex.co", body="B2", is_read=False)

        request = rf.get("/")
        item = _conversations_bell(request)

        assert item["count"] == 2
        assert item["url"] == reverse("cabinet:conversations_inbox")
        assert "New messages" in item["label"]

    def test_provide_conversations_stats(self, rf):
        Message.objects.create(sender_name="S1", sender_email="s1@ex.co", body="B1", status=Message.Status.OPEN)
        Message.objects.create(sender_name="S2", sender_email="s2@ex.co", body="B2", status=Message.Status.PROCESSED)

        request = rf.get("/")
        data = provide_conversations_stats(request)

        stats = data["conversations_stats"]
        assert stats.value == "2"
        assert "waiting: 1" in stats.trend_value
        assert stats.url == reverse("cabinet:conversations_inbox")
