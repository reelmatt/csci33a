from django.contrib import admin

from django.contrib.auth.models import User
from .models import Category, Order, Topping, Item, Status, Size, CartItem

# Admin customization modified from the 'airline4' example in code for
# lecture 8
class ToppingInline(admin.StackedInline):
    model = Topping.allowed_on.through
    extra = 1

class ItemAdmin(admin.ModelAdmin):
    inlines = [ToppingInline]

class ToppingAdmin(admin.ModelAdmin):
    filter_horizontal = ("allowed_on",)

admin.site.register(Category)
admin.site.register(Size)
admin.site.register(Order)
admin.site.register(Topping, ToppingAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(CartItem)
admin.site.register(Status)
