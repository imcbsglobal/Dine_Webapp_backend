from django.urls import path
from .views import login_user, get_all_users,item_master_api

urlpatterns = [
    path('login/', login_user, name='login'),
    path('users/', get_all_users, name='get_all_users'),  # 👈 Added this
    path('items/', item_master_api, name='item_master_api'),
]
