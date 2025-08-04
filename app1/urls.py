from django.urls import path
from .views import login_user, get_all_users

urlpatterns = [
    path('login/', login_user, name='login'),
    path('users/', get_all_users, name='get_all_users'),  # 👈 Added this
]
