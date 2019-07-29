from django.contrib import admin

from django.contrib.auth.models import User
from .models import Category, Order, Topping, Item, Status, Size, CartItem

# Register your models here.
# class ItemInline(admin.StackedInline):
#     model = Item.toppings.through
#
# class ToppingAdmin(admin.ModelAdmin):
#     inlines = [ItemInline]
#
# class ItemAdmin(admin.ModelAdmin):
#     filter_horizontal = ("toppings",)
#
#

admin.site.register(Category)
admin.site.register(Size)
admin.site.register(Order)
admin.site.register(Topping)
admin.site.register(Item)
admin.site.register(CartItem)
admin.site.register(Status)
