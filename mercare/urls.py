from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),          
    path('login/', views.login_view, name='login'), 
    path('registerCustomer/', views.registerCustomer, name='registerCustomer'),
    path('categoriesPage/', views.categoriesPage, name='categoriesPage'),
    path('category/<str:category_slug>/', views.category_detail, name='category_detail'),
]