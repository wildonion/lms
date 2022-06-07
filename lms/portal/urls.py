


from django.urls import path
from .views import create_payment, get_suc_payments, callback, get_payment, get_unsuc_payments, get_payments


urlpatterns = [
    path('purchase/', create_payment),
    path('verify-payment/', callback),
    path('payment/all/successful/', get_suc_payments),
    path('payment/all/unsuccessful/', get_unsuc_payments),
    path('payment/all/', get_payments),
    path('payment/', get_payment),
]