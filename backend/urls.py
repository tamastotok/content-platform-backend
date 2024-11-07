from django.contrib import admin
from django.urls import path, include
from api.views import (
    CreateUserView,
    DeleteUserView,
    EditUserView,
    CustomTokenView,
    csrf_token_view,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/user/register/", CreateUserView.as_view(), name="register"),
    path("api/user/<int:pk>/delete/", DeleteUserView.as_view(), name="delete-user"),
    path("api/user/<int:pk>/edit/", EditUserView.as_view(), name="edit-user"),
    path("api/token/", CustomTokenView.as_view(), name="get_token"),
    path('api/csrf-token/', csrf_token_view, name='csrf-token'),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include("api.urls")),
]
