from django.shortcuts import render

def home(request):
    return render(request, 'landingPage.html')

def login_view(request):
    return render(request, 'registration/login.html')

def registerCustomer(request):
    return render(request, 'registration/registerCustomer.html')

def categoriesPage(request):
    return render(request, 'categoriesPage.html')

def navBar_noLogin(request):
    return render(request, 'components/navBar_noLogin.html')

def footer(request):
    return render(request, 'components/footer.html')

def maternityCare(request):
    return render(request, 'byCategory/maternityCare.html')

def painRelief(request):
    return render(request, 'byCategory/painRelief.html')

def vitaminsSupplements(request):
    return render(request, 'byCategory/vitaminsSupplements.html')