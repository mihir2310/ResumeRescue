from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page, name="home"),  # Home page
    path("upload/", views.upload_form, name="upload"),  # Upload form page
    path("final/", views.final_page, name="final"),  # Final page after form submission
]
