from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listings/create", views.create_listing, name = "create_listing"),
    path("listings/<int:listing_id>", views.view_listing, name = "listing"),
    path("watchlist", views.watchlist_view, name="watchlist"),
    path("listings/<int:listing_id>/watch", views.add_to_watchlist, name="add"),
    path("listings/<int:listing_id>/unwatch", views.remove_from_watchlist, name="remove"),
    path("listings/<int:listing_id>/close", views.close_listing, name = "close_listing"),
    path("listings/<int:listing_id>/comment", views.add_comment, name = "add_comment"),
    path("categories", views.view_categories, name = "categories"),
    path("categories/<str:category>", views.view_category, name = "category")
]
