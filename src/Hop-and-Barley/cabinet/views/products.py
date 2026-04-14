from typing import Any

from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from features.products.models import Category, Product


class ProductCatalogListView(ListView[Product]):
    model = Product
    template_name = "cabinet/products/catalog.html"
    context_object_name = "products"

    def dispatch(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        request.cabinet_module = "products"
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> Any:
        qs = super().get_queryset().select_related("category")
        category_slug = self.request.GET.get("category")
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        return qs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["active_module"] = "products"
        context["categories"] = Category.objects.annotate(product_count=Count("products"))
        context["active_category"] = self.request.GET.get("category")
        context["products_count"] = Product.objects.count()

        # Determine if we should render only the partial for HTMX
        if self.request.headers.get("HX-Request"):
            self.template_name = "cabinet/products/partials/_products_table.html"

        return context


class ProductCreateView(CreateView[Product, Any]):
    model = Product
    fields = ("name", "category", "description", "price", "stock", "image", "is_active")
    template_name = "cabinet/forms/modal_form.html"
    success_url = reverse_lazy("cabinet:product_catalog")

    def dispatch(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        request.cabinet_module = "products"
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: Any) -> Any:
        response = super().form_valid(form)
        if self.request.headers.get("HX-Request"):
            from django.http import HttpResponse

            return HttpResponse(status=204, headers={"HX-Trigger": "products-updated"})
        return response


class ProductUpdateView(UpdateView[Product, Any]):
    model = Product
    fields = ("name", "category", "description", "price", "stock", "image", "is_active")
    template_name = "cabinet/forms/modal_form.html"
    success_url = reverse_lazy("cabinet:product_catalog")

    def dispatch(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        request.cabinet_module = "products"
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: Any) -> Any:
        response = super().form_valid(form)
        if self.request.headers.get("HX-Request"):
            from django.http import HttpResponse

            return HttpResponse(status=204, headers={"HX-Trigger": "products-updated"})
        return response
