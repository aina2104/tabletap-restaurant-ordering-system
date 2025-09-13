"""
forms.py

Defines Django ModelForms for the Tabletap application, mapping form fields to corresponding models.
"""

from django import forms
from .models import *
from django.contrib.auth.models import User

class RestaurantForm(forms.ModelForm):
    """
    Form for creating and updating Restaurant instances.

    Fields:
        Restaurant_Name (str): The display name of the restaurant.
        Table_Amount (int): Number of tables in the restaurant.
    """
    class Meta:
        model = Restaurant
        fields = ['Restaurant_Name', 'Table_Amount']
    

class MenuForm(forms.ModelForm):
    """
    Form for creating and updating Menu instances.

    Fields:
        Menu_Name (str): Name of the menu.
    """
    class Meta:
        model = Menu
        fields = ['Menu_Name']


class CategoryForm(forms.ModelForm):
    """
    Form for creating and updating Menu_Category instances.

    Fields:
        Category_Name (str): Name of the menu category.
    """
    class Meta:
        model = Menu_Category
        fields = ['Category_Name']


class MenuItemForm(forms.ModelForm):
    """
    Form for creating and updating Menu_Item instances.

    Fields:
        Item_Name (str): Name of the food item.
        Description (str): Description of the item.
        Price (Decimal): Unit price of the item.
    """
    class Meta:
        model = Menu_Item
        fields = ['Item_Name', 'Description', 'Price']


class OrderItemForm(forms.ModelForm):
    """
    Form for updating the quantity of an Order_Item.

    Fields:
        Quantity (int): Number of units for the order item.
    """
    class Meta:
        model = Order_Item
        fields = ['Quantity']

