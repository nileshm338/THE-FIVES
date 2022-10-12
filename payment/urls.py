from django.urls import path

from payment import views

urlpatterns = [ path('initiate_payment',views.initiate_payment,name="initiate_payment"),
                path('<str:ref>/',views.verify_payment,name="verify_payment"), ]
