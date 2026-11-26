from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),          
    path('login/', views.login_view, name='login'), 
    path('registerCustomer/', views.registerCustomer, name='registerCustomer'),
    path('categoriesPage/', views.categoriesPage, name='categoriesPage'),
    path('navBar_noLogin/', views.navBar_noLogin, name='navBar_noLogin')
]