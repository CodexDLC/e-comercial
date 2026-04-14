import pytest
from features.products.models import Product
from features.products.services.product import ProductService

@pytest.fixture
def product_factory(db, category):
    def _create(**kwargs):
        defaults = {
            "name": "Test Product",
            "slug": "test-product",
            "price": 100,
            "category": category,
        }
        defaults.update(kwargs)
        return Product.objects.create(**defaults)
    return _create

@pytest.mark.django_db
class TestProductService:
    def test_update_stock(self, product_factory):
        p = product_factory(stock=10)
        ProductService.update_stock(p.id, 50)
        p.refresh_from_db()
        assert p.stock == 50

    def test_toggle_active_status(self, product_factory):
        p = product_factory(is_active=True)
        is_active = ProductService.toggle_active_status(p.id)
        assert is_active is False
        p.refresh_from_db()
        assert p.is_active is False
        
        is_active = ProductService.toggle_active_status(p.id)
        assert is_active is True
        p.refresh_from_db()
        assert p.is_active is True
