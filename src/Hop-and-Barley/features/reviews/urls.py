from django.urls import path

from .views import ReviewCreateView

app_name = "reviews"

urlpatterns = [
    path("<int:product_id>/add/", ReviewCreateView.as_view(), name="add"),
]
