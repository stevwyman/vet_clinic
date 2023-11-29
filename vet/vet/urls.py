from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("client/", include("client.urls")),
    path("admin/", admin.site.urls)
]
