from django.urls import include, path
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.routers import DefaultRouter

from . import views
from .views import CustomUserViewSet

app_name = 'users'

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        LogoutView.as_view(),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(),
        name='login'
    ),
]
