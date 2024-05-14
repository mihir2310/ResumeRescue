from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_page, name="home"),
    path("final/", views.process_files, name="final")
]