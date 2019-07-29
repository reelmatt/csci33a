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
    # sizes = models.ForeignKey(Size, on_delete=models.CASCADE, limit_choices_to={})

    def __str__(self):
        return f"{self.name}"

class Size(models.Model):
    size = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.size}"

# An individual menu item
class Item(models.Model):

    name = models.CharField(max_length=64)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    selected_toppings = models.ManyToManyField(Topping, blank=True, null=True, related_name="items")
    num_toppings = models.IntegerField(validators = [
        MinValueValidator(0),
        MaxValueValidator(5)
    ], default=0)
    price_individual = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    price_small = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    price_large = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    # price_selection = models.ForeignKey(Size, on_delete=models.CASCADE, related_name="items")


    def get_toppings(self):
        return Topping.objects.filter(allowed_on__id__exact=self.id).all()

    def __str__(self):
        return f"{self.name}"

class CartItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="cart_items")
    toppings = models.ManyToManyField(Topping, blank=True, related_name="cart_items")
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name="cart_items")

    def __str__(self):
        return f"{self.item} - {self.size}"

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

    def calculate_cost(self):
        items = self.items.all()
        sum = 0
        for item in items:
            sum += item.item.price_small
        print(f"DO we have items in correct form {items}")
        # self.cost = sum(items)
        print(f"IN CALCULATE COST, value is {sum}")
        self.cost = sum
        return self.cost

    def __str__(self):
        return f"Order #{self.id}"
