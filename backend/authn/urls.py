from django.urls import path

from authn.views import AdminOnlyView, LoginView, LogoutView, MeView, RefreshView, SignupView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("admin-only/", AdminOnlyView.as_view(), name="admin_only"),
]
