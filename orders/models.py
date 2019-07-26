from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


# Name of toppings available
class Topping(models.Model):
    name = models.CharField(max_length=64)
    allowed_on = models.ManyToManyField('Item', blank=True, related_name="toppings")

    def __str__(self):
        return f"{self.name}"

# Section of menu (Pizza, Sicilian, Subs, etc.)
class Category(models.Model):
    name = models.CharField(max_length=64)
    # sizes = models.ForeignKey(Size, on_delete=models.CASCADE, limit_choices_to={})

    def __str__(self):
        return f"{self.name}"

# An individual menu item
class Item(models.Model):
    name = models.CharField(max_length=64)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    # toppings = models.ManyToManyField(Topping, blank=True, related_name="items", limit_choices_to={"allowed": True})
    num_toppings = models.IntegerField(validators = [
        MinValueValidator(0),
        MaxValueValidator(5)
    ], default=0)
    price_individual = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    price_small = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    price_large = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

# A customer's order
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_orders")
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    items = models.ManyToManyField(Item, blank=True, related_name="orders")
    creation_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id}"
