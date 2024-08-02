from django.urls import path
from .views import register_user, user_login, user_logout, deposit, RefreshTokenView, withdraw, check_balance

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('deposit/', deposit, name='deposit'),
    path('withdraw/', withdraw, name='withdraw'),
    path('withdraw/', withdraw, name='withdraw'),
    path('balance/', check_balance ,name='balance'),

    path('api/token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),


]
