import redis
import redis.asyncio

import pytest
from django.contrib.auth import get_user_model
from fakeredis import FakeAsyncRedis, FakeRedis

from features.products.models import Category, Product

# ---------------------------------------------------------------------------
# Global FakeRedis patch — applied at import time so every part of the app
# that uses redis.Redis / redis.asyncio.Redis gets the fake implementation.
# ---------------------------------------------------------------------------
redis.Redis = FakeRedis
redis.from_url = FakeRedis.from_url
redis.asyncio.Redis = FakeAsyncRedis
redis.asyncio.from_url = FakeAsyncRedis.from_url


# ---------------------------------------------------------------------------
# Shared fixtures (available to unit, integration, and e2e test packages)
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username="testuser", password="testpass123", email="test@test.com"
    )


@pytest.fixture
def category(db):
    return Category.objects.create(name="Хмель", slug="khmel")


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        name="Cascade Hops",
        slug="cascade-hops",
        price="15.00",
        stock=100,
        category=category,
        is_active=True,
    )


@pytest.fixture
def auth_client(client, user):
    client.login(username="testuser", password="testpass123")
    return client
