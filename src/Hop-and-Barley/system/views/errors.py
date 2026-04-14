from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def handler404(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(request, "errors/404.html", status=404)


def handler500(request: HttpRequest) -> HttpResponse:
    return render(request, "errors/500.html", status=500)


def handler403(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(request, "errors/403.html", status=403)


def handler400(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(request, "errors/400.html", status=400)
