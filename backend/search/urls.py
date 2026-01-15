from django.urls import path
from . import views

app_name = "search"

urlpatterns = [
    path("", views.search_products, name="search"),
    path("history/", views.search_history, name="history"),
    path("<uuid:search_id>/", views.search_detail, name="detail"),
]
