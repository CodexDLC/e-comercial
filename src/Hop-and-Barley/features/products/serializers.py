from rest_framework import serializers

from .models.category import Category
from .models.product import Product


class CategorySerializer(serializers.ModelSerializer[Category]):
    class Meta:
        model = Category
        fields = (
            "id", "name", "slug", "description",
            "image", "is_featured", "parent"
        )


class ProductSerializer(serializers.ModelSerializer[Product]):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id", "name", "slug", "description",
            "price", "stock", "image", "specifications",
            "category", "is_active", "created_at"
        )
