from django.contrib import admin
from .models import Category, Product
from .models import Pharmacy, Customer, Order

admin.site.register(Category)
admin.site.register(Product)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'phone')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'product', 'pharmacy', 'status', 'created_at')
    list_filter = ('status', 'fulfillment')
    search_fields = ('order_number', 'customer__user__email')