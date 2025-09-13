"""
models.py

Defines the database schema for the Tabletap application, including models for Owners,
Restaurants, Menus, Menu Items, Tables, Orders, and Order Items. Each model corresponds
to a database table and includes fields and relationships.
"""

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.conf import settings
from django.db.models.fields import *
from django.db.models.lookups import *
from django.utils import timezone

class Owner(models.Model):
    """
    Represents an application user who owns one or more restaurants.

    Attributes:
        user (OneToOneField): Links to Django's built-in User model.
        Restaurants (ManyToManyField): The restaurants owned by this owner.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    Restaurants = models.ManyToManyField('Restaurant', through='Restaurant_Owner', blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def save(self, *args, **kwargs):
        if not self.user:  # Check if user is not set
            # Create a default user instance here
            self.user = User.objects.create_user(id=1, username="default_username", password="default_password")
        super().save(*args, **kwargs)


class Restaurant(models.Model):
    """
    Represents a physical restaurant with tables and menus.

    Attributes:
        Restaurant_Name (CharField): Unique name of the restaurant.
        Table_Amount (IntegerField): Number of tables in the restaurant.
        Owners (ManyToManyField): Owners associated via Restaurant_Owner.
    """
    Restaurant_Name = models.CharField(max_length=100, unique=True)
    Table_Amount = models.IntegerField()
    Owners = models.ManyToManyField(Owner, through='Restaurant_Owner')

    def __str__(self):
        return f"{self.Restaurant_Name} with {self.Table_Amount} tables"


class Restaurant_Owner(models.Model):
    """
    Through model linking Owners to Restaurants with a timestamp.

    Attributes:
        Owner_ID (ForeignKey): The owner of the restaurant.
        Restaurant_ID (ForeignKey): The restaurant owned.
        Created_At (DateTimeField): Timestamp when the ownership was created.
    Meta:
        unique_together: Prevent duplicate owner-restaurant links.
    """
    Owner_ID = models.ForeignKey(Owner, on_delete=models.CASCADE)
    Restaurant_ID = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    Created_At = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['Owner_ID', 'Restaurant_ID']

    def __str__(self):
        return f"Owner {self.Owner_ID} owns {self.Restaurant_ID}"


class Menu(models.Model):
    """
    Represents a menu within a restaurant.

    Attributes:
        Menu_Name (CharField): Name of the menu.
        Restaurant_ID (ForeignKey): The restaurant this menu belongs to.
    """
    Menu_Name = models.CharField(max_length=100)
    Restaurant_ID = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return self.Menu_Name


class Menu_Category(models.Model):
    """
    Represents a category within a menu (e.g., appetizers, entrees).

    Attributes:
        Category_Name (CharField): Name of the category.
        Menu_ID (ForeignKey): The menu this category belongs to.
    """
    Category_Name = models.CharField(max_length=100)
    Menu_ID = models.ForeignKey(Menu, on_delete=models.CASCADE)

    def __str__(self):
        return self.Category_Name


class Menu_Item(models.Model):
    """
    Represents an individual item available on a menu category.

    Attributes:
        Item_Name (CharField): Name of the item.
        Description (TextField): Description of the item.
        Price (DecimalField): Cost per unit of the item.
        Category_ID (ForeignKey): Category this item is listed under.
    """
    Item_Name = models.CharField(max_length=100)
    Description = models.TextField()  # blank=True
    Price = models.DecimalField(max_digits=8, decimal_places=2)
    Category_ID = models.ForeignKey(Menu_Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.Item_Name


class Table(models.Model):
    """
    Represents a table in a restaurant.

    Attributes:
        Restaurant_ID (ForeignKey): The restaurant where the table is located.
    """
    Restaurant_ID = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"Table {self.id} at {self.Restaurant_ID.Restaurant_Name}"


class Order(models.Model):
    """
    Represents a customer's order at a restaurant table.

    Attributes:
        Table_ID (ForeignKey): The table placing the order.
        Restaurant_ID (ForeignKey): The restaurant for the order.
        Created_At (DateTimeField): When the order was created.
        Updated_At (DateTimeField): When the order was last updated.
        Completed_Status (BooleanField): Whether the kitchen completed the order.
        Customer_Submitted (BooleanField): Whether the customer submitted it.
        Total_Price (DecimalField): Total cost of all items.
        Order_Items (ManyToManyField): The items in the order via Order_Item.
    """
    Table_ID = models.ForeignKey(Table, on_delete=models.CASCADE, null=True)
    Restaurant_ID = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    Created_At = models.DateTimeField(auto_now_add=True)
    Updated_At = models.DateTimeField(auto_now=True)
    Completed_Status = models.BooleanField(default=False)
    Customer_Submitted = models.BooleanField(default=False)
    Total_Price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Order_Items = models.ManyToManyField(Menu_Item, through='Order_Item')

    def __str__(self):
        return f"Order for Table {self.Table_ID} at Restaurant ID {self.Restaurant_ID} at {self.Created_At}"


class Order_Item(models.Model):
    """
    Represents a customer's Menu Items order with quantities.

    Attributes:
        Order_ID (ForeignKey): The order containing the item.
        Item_ID (ForeignKey): The menu item ordered.
        Quantity (IntegerField): Number of food items ordered.
    Meta:
        unique_together: Ensure each (order, item) pair is unique.
    """
    Order_ID = models.ForeignKey(Order, on_delete=models.CASCADE)
    Item_ID = models.ForeignKey(Menu_Item, on_delete=models.CASCADE)
    Quantity = models.IntegerField()

    class Meta:
        unique_together = ['Order_ID', 'Item_ID']

    def __str__(self):
        return f"Item {self.Item_ID} in Order {self.Order_ID}"