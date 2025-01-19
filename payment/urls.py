from django.urls import path
from . import views

urlpatterns = [
    path('initiate_payment/', views.InitializePaymentView.as_view(), name='initiate_payment'),
    path('verify_payment/', views.CallBack.as_view(), name='verify_payment'),
]