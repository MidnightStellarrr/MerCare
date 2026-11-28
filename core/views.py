from django.shortcuts import render

def home(request):
    return render(request, 'landingPage.html')

def login_view(request):
    return render(request, 'registration/login.html')

def registerCustomer(request):
    return render(request, 'registration/registerCustomer.html')

def categoriesPage(request):
    return render(request, 'categoriesPage.html')

def category_detail(request, category_slug):
    # A dictionary to map URL slugs to display titles
    category_titles = {
        'pain-relief': 'Pain Relief & Fever',
        'maternity-care': 'Baby and Maternity Care',
        'vitamins': 'Vitamins & Supplements',
        'first-aid': 'First Aid & Wound Care',
        'personal-care': 'Personal Care & Hygiene',
        'oral-care': 'Oral Care',
        'medical-equipment': 'Medical Equipment',
        'eye-ear-care': 'Eye and Ear Care',
        'sports-nutrition': 'Sports Nutrition and Fitness',
        'senior-care': 'Senior Care',
    }
    
    # Get the title based on the URL, or default to 'Category'
    category_title = category_titles.get(category_slug, 'Category')

    context = {
        'category_slug': category_slug,
        'category_title': category_title,
    }
    
    # Note: We renamed the template from maternityCare.html to category_detail.html
    return render(request, 'byCategory/category_detail.html', context)