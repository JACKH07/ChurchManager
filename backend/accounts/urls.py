from django.urls import path, include # type: ignore from django.urls
from rest_framework.routers import DefaultRouter # type: ignore from rest_framework.routers         
from rest_framework_simplejwt.views import TokenRefreshView # type: ignore from rest_framework_simplejwt.views
from .views import LoginView, LogoutView, ProfileView, ChangePasswordView, UserViewSet # type: ignore from local app
from churches.views import RegisterChurchView # type: ignore from churches.views

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('register/', RegisterChurchView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('', include(router.urls)),
]
