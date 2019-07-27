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

# An order's status
class Status(models.Model):
    status = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.status}"


# A customer's order
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_orders")
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    items = models.ManyToManyField(Item, blank=True, related_name="orders")
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True, blank=True, related_name="orders")
    creation_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def calculate_cost(self):
        items = self.items.all()
        sum = 0
        for item in items:
            sum += item.price_small
        print(f"DO we have items in correct form {items}")
        # self.cost = sum(items)
        print(f"IN CALCULATE COST, value is {sum}")
        self.cost = sum
        return self.cost

    def __str__(self):
        return f"Order #{self.id}"
