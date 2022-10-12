import requests
from django import forms
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings


# Create your views here.
from payment.models import Payment


def initiate_payment(request:HttpRequest) -> HttpResponse:
    if request.method == "POST":
        payment_form = forms.PaymentForm(request.POST)
        if payment_form.is_valid():
            payment = payment_form.save()
            my_context = {'payment': payment,'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY}
            return render(request,'make_payment.html',my_context)
        else:
            payment_form = forms.PaymentForm()
            context2 = {'payment_form': payment_form}
            return render(request,'payment/initiate_payment.html',context2)

def verify_payment(request:HttpRequest,ref: str) -> HttpResponse:
    payment = get_object_or_404(Payment,ref=ref)
    varified = payment.verify_payment()
    if varified:
        messages.success(request,"Varification Success")
    else:
        messages.error(request,"Varification Failed")
        return redirect('initiate-payment')

class PayStack:
    PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
    base_url = 'https://api.paystack.co'

def verify_payment(self,ref,*args,**kwargs):
    path = f'/transactions/verify/{ref}'

    headers = { "Authorization": f"Bearer {self.PAYSTACK_SECRET_KEY}",'content-Type': 'application/json', }
    url = self.base_url + path
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        return (response_data['status'],response_data['data'])
    response_data = response.json()
    return response_data['status'],response_data['message']




