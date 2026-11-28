from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registerCustomer/', views.registerCustomer, name='registerCustomer'),
    path('step1/', views.step1, name='step1'),
    path('step2/', views.step2, name='step2'),
    path('step3/', views.step3, name='step3'),
    path('step4/', views.step4, name='step4'),
    path('categoriesPage/', views.categoriesPage, name='categoriesPage'),
    path('category/<str:category_slug>/', views.category_detail, name='category_detail'),
    path('account/orders/', views.account_orders, name='account_orders'),
    path('account/orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
]

# Serve uploaded files (product images, pharmacy documents) in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)