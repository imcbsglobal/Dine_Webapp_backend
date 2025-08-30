from django.urls import path
from .views import (
    login_user, 
    get_all_users,
    item_master_api,
    dine_bill_api,
    bill_day_summary,
    DineCancelledBillsAPIView  # Add this new import
)

urlpatterns = [
    path('login/', login_user, name='login'),
    path('users/', get_all_users, name='get_all_users'),
    path('items/', item_master_api, name='item_master_api'),
    path('bills/', dine_bill_api, name='dine_bill_api'),
    path('bill-day-summary/', bill_day_summary, name='bill_day_summary'),
    path('dinecancelledbills/', DineCancelledBillsAPIView.as_view(), name='dine_cancelled_bills_api'),  # NEW endpoint
]