"""
views.py

Defines view functions and class-based views for the Tabletap application.
Handles both owner-facing management (restaurants, menus, categories, items, orders)
and customer-facing ordering flows (QR code generation, menu browsing, cart, order submission).
All views enforce authentication and authorization where appropriate.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import *
from .forms import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import qrcode


def landing_page(request):
    """
    Render the landing page of the application.

    Context:
        title (str): Page title displayed in the template.
    """
    context = {"title": "TableTap"}
    return render(request, "landing_page.html", context)


@login_required
def profile_view(request):
    """
    Display the owner profile page with associated restaurants and menus.

    Retrieves the Owner instance linked to the logged-in user, then
    fetches all restaurants and menus for display.
    """
    owner = Owner.objects.get(user=request.user)
    restaurants = owner.Restaurants.all()
    menus = Menu.objects.all()
    context = {
        "title": "TableTap - Profile",
        "user": request.user,
        "restaurants": restaurants,
        "menus": menus,
    }
    return render(request, "profile_view.html", context)


@login_required
def add_restaurant(request):
    """
    Create a new Restaurant and link it to the current owner.

    On POST: validate and save the RestaurantForm, then create a Restaurant_Owner link.
    On GET: display an empty form.
    """
    if request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            restaurant = form.save()
            owner = Owner.objects.get(user=request.user)
            Restaurant_Owner.objects.create(Owner_ID=owner, Restaurant_ID=restaurant)
            return redirect('profile')  # update as needed
    else:
        form = RestaurantForm()
    return render(request, 'edit_restaurant.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class RestaurantUpdateView(UpdateView):
    """
    Update existing Restaurant details.

    Applies authorization: ensures the logged-in owner owns the restaurant.
    """
    model = Restaurant
    form_class = RestaurantForm
    template_name = 'edit_restaurant.html'
    success_url = reverse_lazy('profile')
    context_object_name = 'restaurant'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('pk')
        owner = Owner.objects.get(user=request.user)
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        return get_object_or_404(Restaurant_Owner, Owner_ID=owner, Restaurant_ID=restaurant)


@login_required
def add_menu(request, restaurant_id):
    """
    Create a new Menu for a given Restaurant.

    Ensures the owner is authorized for the restaurant before allowing creation.
    """
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)  # Get the restaurant
    owner = Owner.objects.get(user=request.user)
    restaurant_owner = get_object_or_404(Restaurant_Owner, Owner_ID=owner, Restaurant_ID=restaurant)  # check authorisation
    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            menu = form.save(commit=False)
            menu.Restaurant_ID = restaurant  # Assign the restaurant to the menu
            menu.save()
            return redirect(reverse_lazy('profile'))  # Redirect to the profile URL
    else:
        form = MenuForm()
    context = {
        'form': form,
        'restaurant_id': restaurant_id,  # Pass restaurant_id for potential use in the template
    }
    return render(request, 'add_menu.html', context)


@method_decorator(login_required, name='dispatch')
class MenuUpdateView(UpdateView):
    """
    Update an existing Menu instance.

    Applies authorization: ensures the logged-in owner owns the restaurant.
    """
    model = Menu
    form_class = MenuForm
    template_name = 'add_menu.html'
    success_url = reverse_lazy('profile')

    def get_queryset(self):
        menu_id = self.kwargs.get('menu_id')
        menu = Menu.objects.get(id=menu_id)
        restaurant = menu.Restaurant_ID
        owner = Owner.objects.get(user=request.user)
        return get_object_or_404(Restaurant_Owner, Owner_ID=owner, Restaurant_ID=restaurant)


@login_required
def dashboard(request, menu_id, category_id):
    """
    Owner dashboard for viewing menus, categories, and items.

    Validates owner authorization, fetches categories and items,
    highlights the active category.
    """
    owner = Owner.objects.get(user=request.user)
    menu = get_object_or_404(Menu, id=menu_id)
    restaurant = menu.Restaurant_ID
    restaurant_owner = get_object_or_404(Restaurant_Owner, Owner_ID=owner, Restaurant_ID=restaurant)  # check authorisation
    categories = Menu_Category.objects.filter(Menu_ID=menu_id)
    if category_id == 0:
        active_category = categories[0] if categories else None
    else:
        category = get_object_or_404(Menu_Category, id=category_id)
        active_category = category
    items = Menu_Item.objects.filter(Category_ID=active_category.id) if active_category else []
    context = {
        "title": "TableTap - Menu",
        "user": request.user,
        "menu": menu,
        "categories": categories,
        "active_category": active_category,
        "items": items,
    }
    return render(request, "dashboard.html", context)


@login_required
def add_category(request, menu_id):
    """
    Create a new Menu_Category under a specific Menu.

    Verifies owner authorization before allowing creation.
    """
    owner = Owner.objects.get(user=request.user)
    menu = get_object_or_404(Menu, id=menu_id)  # Get the menu
    restaurant = menu.Restaurant_ID
    restaurant_owner = get_object_or_404(Restaurant_Owner, Owner_ID=owner, Restaurant_ID=restaurant)  # check authorisation
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.Menu_ID = menu  # Assign the menu to the category
            category.save()
            return redirect(reverse_lazy('owner_menu', kwargs={'menu_id': menu_id, 'category_id': 0,}))
    else:
        form = CategoryForm()
    context = {
        'form': form,
        'menu': menu,  # Pass restaurant_id for potential use in the template
    }
    return render(request, 'add_category.html', context)


@method_decorator(login_required, name='dispatch')
class CategoryUpdateView(UpdateView):
    """
    Update an existing Menu_Category.

    Ensures authorization via queryset filtering.
    """
    model = Menu_Category
    form_class = CategoryForm
    template_name = 'add_category.html'

    def get_queryset(self):
        restaurant = self.object.Menu_ID.Restaurant_ID
        owner = Owner.objects.get(user=request.user)
        return get_object_or_404(Restaurant_Owner, Owner_ID=owner, Restaurant_ID=restaurant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        menu_id = self.object.Menu_ID.id
        context['menu'] = get_object_or_404(Menu, id=menu_id)
        return context

    def get_success_url(self):
        menu_id = self.object.Menu_ID.id
        category_id = self.object.id
        return reverse_lazy('owner_menu', kwargs={'menu_id': menu_id, 'category_id': category_id})


@login_required
def add_menu_item(request, menu_id, category_id):
    """
    Create a new Menu_Item under a specific Menu_Category.

    Verifies owner authorization before allowing creation.
    """
    owner = Owner.objects.get(user=request.user)
    menu = get_object_or_404(Menu, id=menu_id)  # Get the menu
    restaurant = menu.Restaurant_ID
    restaurant_owner = get_object_or_404(Restaurant_Owner, Owner_ID=owner, Restaurant_ID=restaurant)  # check authorisation
    category = get_object_or_404(Menu_Category, id=category_id)  # Get the menu
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.Category_ID = category  # Assign the menu to the category
            item.save()
            return redirect(reverse_lazy('owner_menu', kwargs={'menu_id': menu_id, 'category_id': 0,}))
    else:
        form = MenuItemForm()
    context = {
        'form': form,
        'category': category,  # Pass restaurant_id for potential use in the template
    }
    return render(request, 'add_item.html', context)


@method_decorator(login_required, name='dispatch')
class MenuItemUpdateView(UpdateView):
    """
    Update an existing Menu_Item instance.

    Applies authorization via queryset filtering.
    """
    model = Menu_Item
    form_class = MenuItemForm
    template_name = 'add_item.html'

    def get_queryset(self):
        menu_id = self.kwargs.get('menu_id')
        menu = Menu.objects.get(id=menu_id)
        restaurant = menu.Restaurant_ID
        owner = Owner.objects.get(user=request.user)
        return get_object_or_404(Restaurant_Owner, Owner_ID=owner, Restaurant_ID=restaurant)

    def get_success_url(self):
        menu_id = self.kwargs.get('menu_id')
        category_id = self.kwargs.get('category_id')
        return reverse_lazy('owner_menu', kwargs={'menu_id': menu_id, 'category_id': category_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_id'] = self.kwargs.get('category_id')
        return context


@method_decorator(login_required, name='dispatch')
class MenuDeleteView(DeleteView):
    """
    Delete a Menu belonging to the current owner.
    """
    model = Menu
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('profile')

    def get_queryset(self):
        menu_id = self.kwargs.get('pk')
        menu = Menu.objects.get(id=menu_id)
        restaurant = menu.Restaurant_ID
        owner = Owner.objects.get(user=request.user)
        return get_object_or_404(Restaurant_Owner, Owner_ID=owner, Restaurant_ID=restaurant)


@method_decorator(login_required, name='dispatch')
class CategoryDeleteView(DeleteView):
    """
    Delete a Menu_Category under a Menu the owner controls.
    """
    model = Menu_Category
    template_name = 'delete_category.html'

    def get_queryset(self):
        restaurant = self.object.Menu_ID.Restaurant_ID
        owner = Owner.objects.get(user=request.user)
        return get_object_or_404(Restaurant_Owner, Owner_ID=owner, Restaurant_ID=restaurant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        menu_id = self.object.Menu_ID.id
        category_id = self.kwargs.get('pk')
        context['menu'] = get_object_or_404(Menu, id=menu_id)
        context['category'] = get_object_or_404(Menu_Category, id=category_id)
        return context

    def get_success_url(self):
        menu_id = self.object.Menu_ID.id
        return reverse_lazy('owner_menu', kwargs={'menu_id': menu_id, 'category_id': 0})

@method_decorator(login_required, name='dispatch')
class ItemDeleteView(DeleteView):
    """
    Delete a Menu_Item under a category owned by the user.
    """
    model = Menu_Item
    template_name = 'delete_item.html'

    def get_queryset(self):
        menu_id = self.kwargs.get('menu_id')
        menu = Menu.objects.get(id=menu_id)
        restaurant = menu.Restaurant_ID
        owner = Owner.objects.get(user=request.user)
        return get_object_or_404(Restaurant_Owner, Owner_ID=owner, Restaurant_ID=restaurant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        menu_id = self.kwargs.get('menu_id')
        category = self.object.Category_ID
        item_id = self.kwargs.get('pk')
        context['menu'] = get_object_or_404(Menu, id=menu_id)
        context['category'] = category
        context['item'] = get_object_or_404(Menu_Item, id=item_id)
        return context

    def get_success_url(self):
        menu_id = self.kwargs.get('menu_id')
        category_id = self.kwargs.get('category_id')
        return reverse_lazy('owner_menu', kwargs={'menu_id': menu_id, 'category_id': category_id})


@login_required
def qr_code(request, restaurant_id):
    """
    Generate QR codes for each table in a restaurant.

    Ensures the owner is authorized and creates Table entries as needed.
    Returns URLs embedding table_id, menu_id, and category_id.
    """
    owner = Owner.objects.get(user=request.user)
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    restaurant_owner = get_object_or_404(Restaurant_Owner, Owner_ID=owner, Restaurant_ID=restaurant)  # check authorisation
    table_amount = restaurant.Table_Amount
    tables = Table.objects.filter(Restaurant_ID=restaurant_id)
    if len(tables) < table_amount:
        amount_to_create = table_amount - len(tables)
        for _ in range(amount_to_create):
            new_table = Table(Restaurant_ID=restaurant)
            new_table.save()
    tables = Table.objects.filter(Restaurant_ID=restaurant_id)
    links = []
    menu = Menu.objects.filter(Restaurant_ID=restaurant_id)
    if menu:
        menu = menu[0]
        categories = Menu_Category.objects.filter(Menu_ID=menu.id)
        if categories:
            category = categories[0]
            for i in range(table_amount):
                table = tables[i]
                links.append(f"https://infs3202-2c7cb2f8.uqcloud.net/TableTap/customer/{table.id}/menu/{menu.id}/{category.id}/")
        else:
            menu = []
    context = {
        "title": "TableTap - QR Code",
        "restaurant": restaurant,
        "links": links,
        "menu": menu,
    }
    return render(request, "qr_code.html", context)


def customer_menu(request, table_id, menu_id, category_id):
    """
    Display the customer-facing menu for ordering.

    Shows items and categories for selection at a given table.
    """
    menu = get_object_or_404(Menu, id=menu_id)
    categories = Menu_Category.objects.filter(Menu_ID=menu_id)
    if category_id == 0:
        active_category = categories[0] if categories else None
    else:
        category = get_object_or_404(Menu_Category, id=category_id)
        active_category = category
    items = Menu_Item.objects.filter(Category_ID=active_category.id) if active_category else []
    restaurant = menu.Restaurant_ID
    context = {
        "title": f"{ menu.Menu_Name } Menu",
        "user": request.user,
        "menu": menu,
        "categories": categories,
        "active_category": active_category,
        "items": items,
        "table_id": table_id,
        "restaurant": restaurant,
    }
    return render(request, "menu_customer.html", context)


def all_menus(request, table_id, restaurant_id):
    """
    List all menus for a given restaurant (customer view).
    """
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menus = Menu.objects.filter(Restaurant_ID=restaurant)
    context = {
        "title": f"{restaurant.Restaurant_Name} - All Menus",
        "restaurant": restaurant,
        "menus": menus,
        "table_id": table_id,
    }
    return render(request, "all_menus.html", context)


def add_order_item(request, table_id, menu_id, item_id):
    """
    Add a Menu_Item to the customer's current Order, creating an Order if needed.

    Updates quantity if the item already exists in the order, and recalculates total.
    """
    item = Menu_Item.objects.get(id=item_id)
    order_id = request.session.get('order_id')
    menu = Menu.objects.get(id=menu_id)
    if order_id:
        order = Order.objects.get(id=order_id)
    else:
        table = Table.objects.get(id=table_id)
        order = Order.objects.create(Table_ID=table, Restaurant_ID=menu.Restaurant_ID)
        request.session['order_id'] = order.id
    if request.method == 'POST':
        form = OrderItemForm(request.POST)
        if form.is_valid():
            order_item = form.save(commit=False)
            try:
                existed_item = Order_Item.objects.get(Order_ID=order, Item_ID=item)
                existed_item.Quantity += order_item.Quantity
                existed_item.save()
                order.Total_Price += existed_item.Quantity * item.Price
            except Order_Item.DoesNotExist:
                order_item.Order_ID = order
                order_item.Item_ID = item
                order_item.save()
                order.Total_Price += order_item.Quantity * item.Price
            order.save()
            return redirect(reverse_lazy('customer_menu', kwargs={'table_id': table_id, 'menu_id': menu_id, 'category_id': 0,}))
    else:
        form = OrderItemForm()
    context = {
        'form': form,
        'item': item,
        'table_id': table_id,
        'restaurant_id': menu.Restaurant_ID.id,
        'menu_id': menu_id,
    }
    return render(request, 'add_order_item.html', context)


def view_cart(request, table_id, restaurant_id, menu_id):
    """
    View the current cart (Order) for a customer, and submit the order.

    Displays items with quantities and prices, handles submission to set Customer_Submitted.
    """
    order_id = request.session.get('order_id')
    items = []
    order_total_price = 0
    if order_id:
        order = Order.objects.get(id=order_id)
        order_total_price = order.Total_Price
        order_items = Order_Item.objects.filter(Order_ID=order)
        for item in order_items:
            price = item.Item_ID.Price * item.Quantity
            items.append({
                'Item_Name': item.Item_ID.Item_Name,
                'Quantity': item.Quantity,
                'Price': price,
            })
    if request.method == 'POST':  # handle submit order
        order.Customer_Submitted = True
        order.save()
        return redirect(reverse_lazy('customer_menu', kwargs={'table_id': table_id, 'menu_id': menu_id, 'category_id': 0,}))
    if menu_id == 0:
        restaurant = Restaurant.objects.get(id=restaurant_id)
        menus = Menu.objects.filter(Restaurant_ID=restaurant)
        menu = menus[0]
        menu_id = menu.id
    context = {
        'items': items,
        'table_id': table_id,
        'restaurant_id': restaurant_id,
        'menu_id': menu_id,
        'total_price': order_total_price,
        'order': order,
    }
    return render(request, 'view_cart.html', context)


@login_required
def view_order(request, order_id):
    """
    Owner view for current orders: lists orders and marks them completed.

    Fetches all submitted orders for restaurants owned by the user, and
    allows marking individual orders as completed.
    """
    owner = Owner.objects.get(user=request.user)
    restaurants = owner.Restaurants.all()  # authorisation
    orders = Order.objects.filter(Restaurant_ID__in=restaurants, Customer_Submitted=True, Completed_Status=False)
    items = []
    order = []
    if orders:
        if order_id == 0:
            order_id = orders[0].id
        order = Order.objects.get(id=order_id)
        order_items = Order_Item.objects.filter(Order_ID=order)
        for item in order_items:
            price = item.Item_ID.Price * item.Quantity
            items.append({
                'Item_Name': item.Item_ID.Item_Name,
                'Quantity': item.Quantity,
                'Price': price,
            })
    if request.method == 'POST':  # handle mark as completed
        order.Completed_Status = True
        order.save()
        return redirect(reverse_lazy('view_order', kwargs={'order_id': 0,}))
    context = {
        'items': items,
        'active_order': order,
        'orders': orders,
    }
    return render(request, 'view_order.html', context)