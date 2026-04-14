from django.urls import path

from .views import CartView, CheckoutView, cart_add, cart_remove

app_name = "orders"

urlpatterns = [
    path("cart/", CartView.as_view(), name="cart"),
    path("add/<int:product_id>/", cart_add, name="cart_add"),
    path("remove/<int:product_id>/", cart_remove, name="cart_remove"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
]
