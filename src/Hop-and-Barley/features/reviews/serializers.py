from rest_framework import serializers

from .models.review import Review


class ReviewSerializer(serializers.ModelSerializer[Review]):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Review
        fields = ("id", "product", "user", "username", "rating", "comment", "created_at")
        read_only_fields = ("user",)
