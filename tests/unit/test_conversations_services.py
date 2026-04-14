from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from features.conversations.models import Message, MessageReply
from features.conversations.services.workflow import (
    apply_bulk_action,
    archive_thread,
    create_manual_message,
    create_reply,
    mark_thread_open,
    mark_thread_processed,
    mark_thread_read,
    mark_thread_spam,
    mark_thread_unread,
    trigger_manual_import,
)

User = get_user_model()


@pytest.fixture
def message_factory(db):
    def _create(**kwargs):
        defaults = {
            "sender_name": "Test Sender",
            "sender_email": "sender@example.com",
            "subject": "Test Subject",
            "body": "Test Body",
        }
        defaults.update(kwargs)
        return Message.objects.create(**defaults)

    return _create


@pytest.mark.django_db
class TestConversationWorkflow:
    def test_create_manual_message(self, user):
        message = create_manual_message(
            to_email="customer@example.com", subject="Hello", body="How can I help?", user=user
        )
        assert message.sender_email == "customer@example.com"
        assert message.source == Message.Source.MANUAL
        assert message.replies.count() == 1
        reply = message.replies.first()
        assert reply.body == "How can I help?"
        assert reply.sent_by == user
        assert not reply.is_inbound

    def test_create_reply(self, user, message_factory):
        message = message_factory(status=Message.Status.OPEN, is_read=False)
        with patch("features.conversations.services.workflow.notify_thread_reply") as mock_notify:
            reply = create_reply(message=message, body="Replying here", user=user)

            assert reply.message == message
            assert reply.body == "Replying here"
            assert reply.sent_by == user
            assert not reply.is_inbound

            message.refresh_from_db()
            assert message.status == Message.Status.PROCESSED
            assert message.is_read is True
            mock_notify.assert_called_once_with(message, reply)

    def test_thread_state_updates(self, message_factory):
        msg = message_factory(is_read=False, status=Message.Status.OPEN)

        mark_thread_read(message=msg)
        assert msg.is_read is True

        mark_thread_unread(message=msg)
        assert msg.is_read is False

        mark_thread_processed(message=msg)
        assert msg.status == Message.Status.PROCESSED
        assert msg.is_read is True

        mark_thread_open(message=msg)
        assert msg.status == Message.Status.OPEN

        mark_thread_spam(message=msg)
        assert msg.status == Message.Status.SPAM
        assert msg.is_read is True

        archive_thread(message=msg)
        assert msg.is_archived is True
        assert msg.is_read is True

    def test_apply_bulk_action(self, message_factory):
        msgs = [message_factory() for _ in range(3)]
        count = apply_bulk_action(messages=msgs, action="mark_read")
        assert count == 3
        for m in msgs:
            m.refresh_from_db()
            assert m.is_read is True

    def test_apply_bulk_action_invalid(self, message_factory):
        msg = message_factory()
        with pytest.raises(ValueError, match="Unsupported bulk action"):
            apply_bulk_action(messages=[msg], action="invalid_action")

    def test_trigger_manual_import(self):
        with patch("features.conversations.services.workflow.trigger_email_import") as mock_import:
            mock_import.return_value = {"mode": "thread"}
            res = trigger_manual_import()
            assert res["ok"] is True
            assert res["code"] == "email-import-thread"

            mock_import.return_value = {"mode": "queued"}
            res = trigger_manual_import()
            assert res["code"] == "email-import-queued"


@pytest.mark.django_db
class TestConversationAlerts:
    def test_build_subject(self, message_factory):
        from features.conversations.services.alerts import _build_subject

        msg = message_factory(sender_name="Alice", subject="Hi")
        assert "Alice" in _build_subject(msg)
        assert "Hi" in _build_subject(msg)

        msg2 = message_factory(sender_name="Bob", subject="", body="Hello there world")
        assert "Bob" in _build_subject(msg2)
        assert "Hello there" in _build_subject(msg2)

    def test_build_reply_subject(self, message_factory):
        from features.conversations.services.alerts import _build_reply_subject

        msg = message_factory(subject="Support")
        assert _build_reply_subject(msg) == "Re: Support"

        msg2 = message_factory(subject="Re: Support")
        assert _build_reply_subject(msg2) == "Re: Support"

        msg3 = message_factory(subject="")
        assert "Re: Conversation" in _build_reply_subject(msg3)

    def test_notify_new_message(self, message_factory):
        from features.conversations.services.alerts import notify_new_message

        msg = message_factory()
        with patch("features.conversations.services.alerts._get_notification_engine") as mock_engine:
            notify_new_message(msg)
            mock_engine.return_value.dispatch_event.assert_called_once_with("conversations.new_message", msg)

    def test_notify_thread_reply(self, message_factory, user):
        from features.conversations.services.alerts import notify_thread_reply

        msg = message_factory()
        reply = MessageReply.objects.create(message=msg, body="Reply", sent_by=user)
        with patch("features.conversations.services.alerts._get_notification_engine") as mock_engine:
            notify_thread_reply(msg, reply)
            mock_engine.return_value.dispatch_event.assert_called_once_with("conversations.thread_reply", msg, reply)
