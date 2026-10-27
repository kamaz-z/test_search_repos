from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from search.auth_views import LoginView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login", LoginView.as_view(), name="login"),
    path("api/register/", obtain_auth_token),

    path("api/", include("search.urls")),
]