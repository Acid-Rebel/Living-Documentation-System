from django.urls import path, re_path

from . import views


urlpatterns = [
    path("health/", views.health_view, name="health"),
    path("items/<int:item_id>/", views.ItemDetailView.as_view(), name="item-detail"),
    re_path(r"^legacy/$", views.legacy_view, name="legacy"),
]

urlpatterns += [
    path("status/", views.status_view),
]
