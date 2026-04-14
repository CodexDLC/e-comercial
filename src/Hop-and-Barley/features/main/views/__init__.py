from typing import Any

from django import forms
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from features.conversations.forms.contact import ContactForm
from features.products.models import Category
from features.products.views.catalog import ProductListView


class HomeView(ProductListView):
    template_name = "features/main/home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # Fetch exactly 3 featured categories for the Bento layout
        context["featured_categories"] = Category.objects.filter(is_active=True, is_featured=True)[:3]
        return context


class ContactsView(TemplateView):
    template_name = "features/main/contacts.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        form = ContactForm()
        # Add CSS classes dynamically to keep conversations/ forms clean
        for field in form.fields.values():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({"class": "form-textarea", "placeholder": field.label})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({"class": "form-select"})
            else:
                field.widget.attrs.update({"class": "form-input", "placeholder": field.label})
        context["form"] = form
        return context

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Your message has been sent successfully. We will get back to you soon!"))
            return redirect(reverse("main:contacts"))

        context = self.get_context_data(**kwargs)
        context["form"] = form
        return self.render_to_response(context)


class GuidesRecipesView(TemplateView):
    template_name = "features/main/guides_recipes.html"


class CommunityView(TemplateView):
    template_name = "features/main/community.html"


class ResourcesView(TemplateView):
    template_name = "features/main/resources.html"
