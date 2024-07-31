from django.urls import path
from .views import register_user, user_login, user_logout, deposit, RefreshTokenView, withdraw

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('deposit/', deposit, name='deposit'),
    path('withdraw/', withdraw, name='withdraw'),
    path('api/token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),

]
