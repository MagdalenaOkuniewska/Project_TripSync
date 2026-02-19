from django.urls import path
from .views.shopping_list_views import (
    ShoppingListCreateView,
    ShoppingListDetailView,
    ShoppingListDeleteView,
    toggle_item_purchased,
)
from .views.shopping_item_views import (
    ShoppingItemCreateView,
    ShoppingItemUpdateView,
    ShoppingItemDeleteView,
)

urlpatterns = [
    # Shopping List
    path(
        "trips/<int:trip_pk>/create/",
        ShoppingListCreateView.as_view(),
        name="shopping-list-create",
    ),
    path("<int:pk>/", ShoppingListDetailView.as_view(), name="shopping-list-details"),
    path(
        "<int:pk>/delete/",
        ShoppingListDeleteView.as_view(),
        name="shopping-list-delete",
    ),
    # Shopping Items
    path(
        "<int:shopping_list_pk>/items/create/",
        ShoppingItemCreateView.as_view(),
        name="shopping-item-create",
    ),
    path(
        "items/<int:pk>/update/",
        ShoppingItemUpdateView.as_view(),
        name="shopping-item-update",
    ),
    path(
        "items/<int:pk>/delete/",
        ShoppingItemDeleteView.as_view(),
        name="shopping-item-delete",
    ),
    # Toggle purchased (AJAX)
    path(
        "items/<int:item_id>/toggle/",
        toggle_item_purchased,
        name="shopping-item-toggle",
    ),
]
