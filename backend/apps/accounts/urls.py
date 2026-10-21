from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CurrentUserProfileView,
    CustomTokenObtainPairView,
    QuickRoleSwitchView,
    SignWaiverView,
)

# This list serves to define authentication and RBAC profile endpoints.
urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("demo-role-login/", QuickRoleSwitchView.as_view(), name="demo_role_login"),
    path("me/", CurrentUserProfileView.as_view(), name="current_user_profile"),
    path("sign-waiver/", SignWaiverView.as_view(), name="sign_waiver"),
]