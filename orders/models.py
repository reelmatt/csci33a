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
    add_on_cost = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

# Size options for Items
class Size(models.Model):
    size = models.CharField(max_length=32)

    def __str__(self):
        return f"price_{self.size}"

# An individual menu item
class Item(models.Model):
    name = models.CharField(max_length=64)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    num_toppings = models.IntegerField(validators = [
        MinValueValidator(0),
        MaxValueValidator(5)
    ], default=0)
    price_individual = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    price_small = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    price_large = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

# A CartItem can contain many (menu) Items
class CartItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="cart_items")
    toppings = models.ManyToManyField(Topping, blank=True, related_name="cart_items")
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name="cart_items")

    # Add the cost of the item and any additional topping costs
    def cost(self):
        base_cost = getattr(self.item, f"{self.size}")

        if self.item.category.add_on_cost:
            add_on_cost = self.item.category.add_on_cost * len(self.toppings.all())
        else:
            add_on_cost = 0

        return base_cost + add_on_cost

    # Format the topping list in a human-readable string
    def topping_list(self):
        toppings = []
        for topping in self.toppings.all():
            toppings.append(topping.name)

        if len(toppings) > 0:
            return f"with {', '.join(toppings)}"
        else:
            return ""

    def __str__(self):
        return f"{self.item.category}, {self.item} ({self.size.size}) {self.topping_list()} - ${self.cost()}"

# An order's status
class Status(models.Model):
    status = models.CharField(max_length=32)
    friendly_status = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.friendly_status}"

# A customer's order
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_orders")
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    items = models.ManyToManyField(CartItem, blank=True, related_name="orders")
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True, blank=True, related_name="orders")
    creation_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id}"
