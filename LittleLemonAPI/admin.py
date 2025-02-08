from django.contrib import admin
from .models import Category, MenuItem, Cart, Order, OrderItems

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)} 
    

admin.site.register(Category, CategoryAdmin)

admin.site.register(MenuItem)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItems)