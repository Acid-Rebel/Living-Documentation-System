from django.urls import path

from . import views


urlpatterns = [
    path("status/", views.status_view, name="status"),
    path("items/<int:item_id>/", views.item_detail_view, name="item-detail"),
]
