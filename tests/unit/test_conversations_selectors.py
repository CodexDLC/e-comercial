import pytest
from django.http import Http404

from features.conversations.models import Message, MessageReply
from features.conversations.selector.messages import (
    get_message,
    get_message_or_404,
    get_messages,
    get_paginated_messages,
    get_replies,
    get_status_counts,
    get_topic_counts,
    get_unread_count,
)


@pytest.fixture
def message_factory(db):
    def _create(**kwargs):
        defaults = {
            "sender_name": "Test",
            "sender_email": "test@example.com",
            "body": "Body",
        }
        defaults.update(kwargs)
        return Message.objects.create(**defaults)

    return _create


@pytest.mark.unit
@pytest.mark.django_db
class TestConversationSelectors:
    def test_get_messages_filtering(self, message_factory):
        _m1 = message_factory(status=Message.Status.OPEN, topic=Message.Topic.PRODUCT)
        _m2 = message_factory(status=Message.Status.PROCESSED, topic=Message.Topic.ORDER)
        _m3 = message_factory(is_archived=True)

        assert get_messages().count() == 2
        assert get_messages(status=Message.Status.OPEN).count() == 1
        assert get_messages(topic=Message.Topic.ORDER).count() == 1

    def test_get_message_selectors(self, message_factory):
        m1 = message_factory()
        m2 = message_factory(is_archived=True)

        assert get_message(m1.pk) == m1
        assert get_message(m2.pk) is None
        assert get_message_or_404(m1.pk) == m1

        with pytest.raises(Http404):
            get_message_or_404(m2.pk)

    def test_get_replies(self, message_factory):
        m1 = message_factory()
        MessageReply.objects.create(message=m1, body="R1")
        MessageReply.objects.create(message=m1, body="R2")

        replies = get_replies(m1.pk)
        assert replies.count() == 2
        assert replies[0].body == "R1"

    def test_counts_selectors(self, db, message_factory):
        # Isolation: Ensure we start with 0 messages
        from features.conversations.models import Message

        Message.objects.all().delete()
        assert Message.objects.count() == 0

        message_factory(status=Message.Status.OPEN, topic=Message.Topic.PRODUCT, is_read=False)
        message_factory(status=Message.Status.PROCESSED, topic=Message.Topic.PRODUCT, is_read=True)
        message_factory(status=Message.Status.SPAM, topic=Message.Topic.OTHER, is_read=True)

        topic_counts = get_topic_counts()
        assert len(topic_counts) == 1
        assert topic_counts[0]["topic"] == Message.Topic.PRODUCT
        assert topic_counts[0]["count"] == 2

        status_counts = get_status_counts()
        assert status_counts["open"] == 1
        assert status_counts["processed"] == 1
        assert status_counts["spam"] == 1

        assert get_unread_count() == 1

    def test_paginated_messages(self, message_factory):
        for _ in range(5):
            message_factory()

        page = get_paginated_messages(per_page=2)
        assert len(page) == 2
        assert page.paginator.count == 5
