from django.urls import path
from . import views

urlpatterns = [
    path("", views.cms_start, name="cms_start"),
]