from django.shortcuts import render

def home(request):
    return render(request, 'landingPage.html')

def login_view(request):
    return render(request, 'registration/login.html')

def registerCustomer(request):
    return render(request, 'registration/registerCustomer.html')