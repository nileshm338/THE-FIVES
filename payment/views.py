from django.shortcuts import render
import razorpay
from django.views.decorators.csrf import csrf_exempt


def home1(request):
    if request.method == "POST":
        amount = 50000
        order_currency ='INR'
        client = razorpay.Client(auth=("rzp_test_8EiJB8PVDBESjp", "uV2PFeI9ziq7QfpT0wXQvNTT"))
        payment = client.order.create({'amount': amount, 'currency': 'INR','payment_capture': '1'})
    return render(request, 'payment/index1.html')

@csrf_exempt
def success(request):
    return render(request, "payment/success.html")