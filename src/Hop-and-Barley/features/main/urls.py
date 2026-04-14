from django.urls import path

from .views import (
    CommunityView,
    ContactsView,
    GuidesRecipesView,
    HomeView,
    ResourcesView,
)

app_name = "main"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
    path("guides-recipes/", GuidesRecipesView.as_view(), name="guides-recipes"),
    path("community/", CommunityView.as_view(), name="community"),
    path("resources/", ResourcesView.as_view(), name="resources"),
]
