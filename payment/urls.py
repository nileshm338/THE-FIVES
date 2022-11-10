from django.urls import path
from .views import home1, success

urlpatterns = [
    path('payment/', home1, name='home1'),
     path('payment/success' , success , name='success')
]