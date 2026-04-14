from typing import TYPE_CHECKING, cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views import View

from features.products.models import Product
from features.reviews.models import Review

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class ReviewCreateView(LoginRequiredMixin, View):
    http_method_names = ("post",)

    def post(self, request: HttpRequest, product_id: int) -> HttpResponse:

        product = get_object_or_404(Product, id=product_id, is_active=True)

        if Review.objects.filter(product=product, user=cast("User", request.user)).exists():
            if request.headers.get("HX-Request"):
                return HttpResponse(status=409)
            return redirect("products:detail", slug=product.slug)

        rating = request.POST.get("rating")
        comment = request.POST.get("comment", "").strip()

        if not rating or not comment:
            if request.headers.get("HX-Request"):
                return HttpResponse(status=400)
            return redirect("products:detail", slug=product.slug)

        Review.objects.create(
            product=product,
            user=cast("User", request.user),
            rating=int(rating),
            comment=comment,
        )

        if request.headers.get("HX-Request"):
            reviews = product.reviews.all()[:3]
            html = render_to_string(
                "features/reviews/partials/_reviews_section.html",
                {"product": product, "reviews": reviews, "has_review": True},
                request=request,
            )
            response = HttpResponse(html)
            response["HX-Trigger"] = "reviewAdded"
            return response

        return redirect("products:detail", slug=product.slug)
