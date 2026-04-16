from typing import Any

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, View

from features.products.models import Product

from .cart import Cart
from .services.order import OrderService


class CartView(TemplateView):
    template_name = "features/orders/cart.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["cart"] = Cart(self.request.session)
        return context


@require_POST
def cart_add(request: HttpRequest, product_id: int) -> HttpResponse:
    cart = Cart(request.session)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get("quantity", 1))
    override = request.POST.get("override", "False") == "True"

    if product.stock < quantity:
        messages.error(request, _("Not enough items in stock."))
    else:
        cart.add(product=product, quantity=quantity, override_quantity=override)
        if override:
            messages.success(request, _("Cart updated."))
        else:
            messages.success(request, _("Product added to cart."))

    return redirect("orders:cart")


@require_POST
def cart_remove(request: HttpRequest, product_id: int) -> HttpResponse:
    cart = Cart(request.session)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, _("Product removed from cart."))
    return redirect("orders:cart")


class CheckoutView(View):
    template_name = "features/orders/checkout.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        cart = Cart(request.session)
        if len(cart) == 0:
            messages.warning(request, _("Your cart is empty."))
            return redirect("products:list")
        return render(request, self.template_name, {"cart": cart})

    def post(self, request: HttpRequest) -> HttpResponse:
        cart = Cart(request.session)
        # Basic logic for creating order
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        if not all([full_name, email, phone, address]):
            messages.error(request, _("Please fill in all required fields."))
            return render(request, self.template_name, {"cart": cart})

        order = OrderService.create_order(
            user=request.user,
            cart=cart,
            full_name=full_name,
            email=email,
            phone=str(phone),
            address=address,
        )

        messages.success(request, _("Order placed successfully!"))
        return redirect("orders:success", order_id=order.id)


class OrderSuccessView(TemplateView):
    template_name = "features/orders/success.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        from .models.order import Order

        context["order"] = get_object_or_404(Order, id=kwargs["order_id"])
        return context
