from django.contrib import admin
from django.urls import path, include
from api.views import CreateUserView, CustomTokenView, csrf_token_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/user/register/", CreateUserView.as_view(), name="register"),
    path("api/token/", CustomTokenView.as_view(), name="get_token"),
    path('api/csrf-token/', csrf_token_view, name='csrf-token'),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include("api.urls")),
]
