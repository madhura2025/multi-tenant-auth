from django.urls import path

from simpleauth.views import SimpleLoginView

urlpatterns = [
    path("login/", SimpleLoginView.as_view(), name="simple_login"),
]
