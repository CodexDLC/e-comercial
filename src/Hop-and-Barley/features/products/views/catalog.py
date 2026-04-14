from typing import Any

from django.db.models import Avg, Q, QuerySet
from django.views.generic import DetailView, ListView

from features.orders.cart import Cart
from features.products.models import Category, Product
from features.reviews.models import Review


class ProductListView(ListView[Product]):
    model = Product
    template_name = "features/products/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self) -> QuerySet[Product]:
        queryset = super().get_queryset().filter(is_active=True).annotate(avg_rating=Avg("reviews__rating"))

        # Category filtering (multiple)
        category_slugs = self.request.GET.getlist("category")
        if category_slugs:
            queryset = queryset.filter(category__slug__in=category_slugs)

        # Search filtering
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))

        # Sorting
        sort = self.request.GET.get("sort")
        if sort == "price_asc":
            queryset = queryset.order_by("price")
        elif sort == "price_desc":
            queryset = queryset.order_by("-price")
        elif sort == "rating":
            queryset = queryset.order_by("-avg_rating")
        else:
            queryset = queryset.order_by("-created_at")

        return queryset.distinct()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(is_active=True).order_by("order")
        context["selected_categories"] = self.request.GET.getlist("category")
        context["cart"] = Cart(self.request.session)
        return context


class ProductDetailView(DetailView[Product]):
    model = Product
    template_name = "features/products/product_detail.html"
    context_object_name = "product"

    def get_queryset(self) -> QuerySet[Product]:
        return super().get_queryset().filter(is_active=True)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["cart"] = Cart(self.request.session)
        if self.request.user.is_authenticated:
            context["has_review"] = Review.objects.filter(product=self.object, user=self.request.user).exists()
        else:
            context["has_review"] = False
        return context
