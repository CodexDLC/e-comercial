import pytest

from features.products.context_processors import categories
from features.products.models import Category


@pytest.mark.unit
@pytest.mark.django_db
def test_categories_context_processor(rf):
    Category.objects.create(name="Active 1", slug="a1", is_active=True, order=2)
    Category.objects.create(name="Active 2", slug="a2", is_active=True, order=1)
    Category.objects.create(name="Inactive", slug="i", is_active=False)

    request = rf.get("/")
    context = categories(request)

    cats = list(context["all_categories"])
    assert len(cats) == 2
    assert cats[0].slug == "a2"  # Due to ordering
    assert cats[1].slug == "a1"
    assert not any(c.slug == "i" for c in cats)
