import functools
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q, Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import bakery_models, order
from .models import bakery_models, register_model, customer, order
from .forms import bakery_forms, register_forms, Login_form,ResetPasswordForm

logger = logging.getLogger(__name__)

def get_logged_in_user(request):
    """Return the register_model instance for the current session, or None."""
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return register_model.objects.get(pk=user_id)
    except register_model.DoesNotExist:
        request.session.flush()
        return None


def login_required(view_fn):
    """Decorator: redirect to login if no valid session exists."""
    @functools.wraps(view_fn)
    def wrapper(request, *args, **kwargs):
        if not get_logged_in_user(request):
            request.session.pop('success_message', None)
            request.session.pop('error_message', None)
            request.session['error_message'] = "Please log in to continue."
            return redirect('login')
        return view_fn(request, *args, **kwargs)
    return wrapper


def admin_required(view_fn):
    """Decorator: allow only logged-in admin users (session-based or Django admin auth)."""
    @functools.wraps(view_fn)
    def wrapper(request, *args, **kwargs):
        # Allow if logged in via Django's built-in admin
        logger.warning("DEBUG: user=%s authenticated=%s is_staff=%s session_keys=%s",
            request.user, request.user.is_authenticated,
            getattr(request.user, 'is_staff', False), list(request.session.keys()))
        if request.user.is_authenticated and request.user.is_staff:
            return view_fn(request, *args, **kwargs)
        # Allow if logged in via custom session and is_admin
        user = get_logged_in_user(request)
        if not user:
            request.session['error_message'] = "Please log in to continue."
            return redirect('login')
        is_admin = getattr(user, 'is_admin', False)
        request.session['is_admin'] = is_admin
        if is_admin:
            return view_fn(request, *args, **kwargs)
        request.session['error_message'] = "You do not have permission to access this page."
        return redirect('base')
    return wrapper


def register_view(request):
    if get_logged_in_user(request):
        return redirect('base')
    if request.method == 'POST':
        form = register_forms(request.POST)
        if form.is_valid():
            username = form.cleaned_data['Username']
            email    = form.cleaned_data['Email']
            password = make_password(form.cleaned_data['Password'])
            register_model.objects.create(Username=username, Email=email, Password=password)
            request.session['success_message'] = "Registration successful. Please log in."
            return redirect('login')
    else:
        form = register_forms()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if get_logged_in_user(request):
        if request.session.get('is_admin'):
            return redirect('admin_dashboard')
        return redirect('base')
    form = Login_form()
    if request.method == 'POST':
        form = Login_form(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = register_model.objects.get(Username=username)
            except register_model.DoesNotExist:
                user = None

            dummy_hash = make_password('dummy_prevent_timing')
            valid = check_password(password, user.Password if user else dummy_hash)

            if user and valid:
                logger.info("LOGIN SUCCESS: user='%s' ip=%s", username, request.META.get('REMOTE_ADDR'))
                request.session.cycle_key()
                request.session['user_id']  = user.pk
                request.session['username'] = user.Username
                request.session['is_admin'] = getattr(user, 'is_admin', False)
                request.session['success_message'] = f"Welcome back, {user.Username}!"
                if getattr(user, 'is_admin', False):
                    return redirect('admin_dashboard')
                return redirect('base')
            else:
                logger.warning("LOGIN FAILED: user='%s' ip=%s", username, request.META.get('REMOTE_ADDR'))
                request.session['error_message'] = "Invalid username or password."

    success_message = request.session.pop('success_message', None)
    error_message   = request.session.pop('error_message', None)
    return render(request, 'login.html', {'form': form, 'success_message': success_message, 'error_message': error_message})


def logout_view(request):
    request.session.flush()
    request.session['success_message'] = "You have been logged out."
    return redirect('login')

def forgot_password(request):
    error_message = request.session.pop('error_message', None)
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = register_model.objects.get(Email=email)
            request.session['reset_email'] = user.Email
            return redirect('reset_password')
        except register_model.DoesNotExist:
            request.session['error_message'] = "Email not found"
            return render(request, 'forgot_password.html')
    return render(request, 'forgot_password.html', {
        'error_message': error_message
    })

def reset_password(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')
    success_message = request.session.pop('success_message', None)
    error_message = request.session.pop('error_message', None)
    if request.method == "POST":
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password == confirm_password:
            user = register_model.objects.get(Email=email)
            user.Password = make_password(new_password)
            user.save()
            request.session['success_message'] = "Password updated successfully"
            return redirect('login')
        else:
            request.session['error_message'] = "Passwords do not match"
            return redirect('reset_password')

    return render(request, 'reset_password.html', {
        'success_message': success_message,
        'error_message': error_message
    })


def about(request):
    return render(request, 'about.html')

def reviews(request):
    return render(request, 'reviews.html')

def contact(request):
    return render(request, 'contact.html')

def careers(request):
    return render(request, 'careers.html')



def customize_cake(request):
    return render(request, 'customize_cake.html')

def custom_gifts(request):
    return render(request, 'custom_gifts.html')

def corporate_orders(request):
    return render(request, 'corporate_orders.html')

def support(request):
    return render(request, 'support.html')




def faqs(request):
    return render(request, 'faqs.html')

def shipping_delivery(request):
    return render(request, 'shipping_delivery.html')

def return_policy(request):
    return render(request, 'return_policy.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_condition(request):
    return render(request, 'terms_condition.html')

def blog(request):
    return render(request, 'blog.html')



def gifts_to_mother(request):
    return render(request, 'gifts_to_mother.html')

def birthday_cakes(request):
    return render(request, 'birthday_cakes.html')

def anniversary_cakes(request):
    return render(request, 'anniversary_cakes.html')

def first_anniversary_gifts(request):
    return render(request, 'first_anniversary_gifts.html')

def twentyfive_anniversary_gifts(request):
    return render(request, 'twentyfive_anniversary_gifts.html')

def baby_boy_cakes(request):
    return render(request, 'baby_boy_cakes.html')

def baby_girl_cakes(request):
    return render(request, 'baby_girl_cakes.html')




def mothers_day_gifts(request):
    return render(request, 'mothers_day_gifts.html')

def parents_day_gifts(request):
    return render(request, 'parents_day_gifts.html')

def friendship_day_gifts(request):
    return render(request, 'friendship_day_gifts.html')

def rakhi_gifts(request):
    return render(request, 'rakhi_gifts.html')

def christmas_gifts(request):
    return render(request, 'christmas_gifts.html')

def new_year_gifts(request):
    return render(request, 'new_year_gifts.html')

def valentines_day_gifts(request):
    return render(request, 'valentines_day_gifts.html')

@admin_required
def admin_dashboard(request):
    total_products  = bakery_models.objects.count()
    total_customers = register_model.objects.count()
    total_orders    = order.objects.count()
    total_revenue   = order.objects.filter(status='Delivered').aggregate(rev=Sum('total_price'))['rev'] or 0

    all_products  = bakery_models.objects.all()
    all_orders    = order.objects.select_related('customer', 'products').order_by('-created_at')
    all_customers = register_model.objects.all()

    pending_count   = order.objects.filter(status='Pending').count()
    preparing_count = order.objects.filter(status='Preparing').count()
    ofd_count       = order.objects.filter(status='Out for Delivery').count()
    delivered_count = order.objects.filter(status='Delivered').count()
    
    success_message = request.session.pop('success_message', None)
    error_message = request.session.pop('error_message', None)
    

    return render(request, 'admin_dashboard.html', {
        'total_products':  total_products,
        'total_customers': total_customers,
        'total_orders':    total_orders,
        'total_revenue':   total_revenue,
        'all_products':    all_products,
        'all_orders':      all_orders,
        'all_customers':   all_customers,
        'pending_count':   pending_count,
        'preparing_count': preparing_count,
        'ofd_count':       ofd_count,
        'delivered_count': delivered_count,
        'success_message': success_message,
        'error_message': error_message,
    })

@admin_required
def admin_update_order_status(request, order_id):
    if request.method == 'POST':
        o = get_object_or_404(order, id=order_id)
        new_status = request.POST.get('status')
        valid_statuses = [choice[0] for choice in order.STATUS]
        if new_status in valid_statuses:
            o.status = new_status
            o.save()
            request.session['success_message'] = f"Order #{order_id} status updated."
        else:
            request.session['error_message'] = "Invalid status value."

    return redirect('admin_dashboard')

@admin_required
def admin_delete_product(request, product_id):
    product = get_object_or_404(bakery_models, id=product_id)
    product.delete()
    request.session['success_message'] = "Product deleted successfully."
    return redirect('admin_dashboard')


def base_view(request):
    # Admins should always land on the admin dashboard
    if request.session.get('is_admin'):
        return redirect('admin_dashboard')
    error_message = request.session.pop('error_message', None)
    items = bakery_models.objects.all()
    best_sellers = bakery_models.objects.filter(Items__in=[
        'BlackForest',    
        'Macarons',
        'Brownie Muffin',
        
    ])

    most_loved = bakery_models.objects.filter(Items__in=[
        'Oreo Milkshake',
        'BBQ pizza',
        'Fruit Tarts',
    ])
    return render(request, 'base.html', {'items': items, 'best_sellers': best_sellers, 'most_loved': most_loved,'error_message': error_message,})


@login_required
def create_view(request):
    
    if not request.user.is_staff:
        return HttpResponseForbidden("Only admin can add items")
    data = bakery_forms()
    
    if request.method == "POST":

        data =bakery_forms(request.POST, request.FILES)

        if data.is_valid():
            data.save()
            return redirect('admin_dashboard')

    return render(request, 'create.html', {'data': data})


def filter_view(request, id):
    data2 = get_object_or_404(bakery_models, id=id)
    return render(request, 'filter.html', {'data2': data2})


@login_required
def update_view(request, id):
    data3 = get_object_or_404(bakery_models, id=id)
    if request.method == 'POST':
        form = bakery_forms(request.POST, request.FILES, instance=data3)
        if form.is_valid():
            form.save()
            return redirect('base')
    else:
        form = bakery_forms(instance=data3)
    return render(request, 'update.html', {'data4': form})


@login_required
def delete_view(request, id):
    data5 = get_object_or_404(bakery_models, id=id)
    data5.delete()
    return redirect('base')


def fili(request, Name):
    sort = request.GET.get('sort', '')
    data6 = bakery_models.objects.filter(Name__iexact=Name)
    if sort == 'price_asc':
        data6 = data6.order_by('Price')
    elif sort == 'price_desc':
        data6 = data6.order_by('-Price')
    elif sort == 'newest':
        data6 = data6.order_by('-id')
    return render(request, 'filt.html', {'data6': data6, 'category_name': Name, 'current_sort': sort})


def search_view(request):
    query   = request.GET.get('q', '').strip()
    results =bakery_models.objects.none()
    if query:
        results = bakery_models.objects.filter(
            Q(Name__icontains=query) | Q(Items__icontains=query)
        ).order_by('Name')
    return render(request, 'search_results.html', {'results': results, 'query': query,})


@login_required
def add_to_cart(request, item_id):
    if request.method == "POST":
        try:
            item     = get_object_or_404(bakery_models, id=item_id)
            quantity = int(request.POST.get('quantity', 1))

            if quantity <= 0:
                request.session['error_message'] = "Quantity must be at least 1."
                return redirect('base')

            cart     = request.session.get('cart', {})
            item_key = str(item_id)

            if item_key in cart:
                cart[item_key]['quantity'] += quantity
            else:
                cart[item_key] = {
                    'Name':     item.Name,
                    'Price':    float(item.Price),
                    'quantity': quantity,
                    'Image':    item.Image.url if item.Image else '',
                }

            request.session['cart']    = cart
            request.session.modified   = True
            request.session['success_message'] = f"Added {quantity} × {item.Name} to cart."
        except (ValueError, TypeError):
            request.session['error_message'] = "Invalid quantity."
        except Exception:
            request.session['error_message'] = "Could not add item to cart."
    return redirect('view_cart')


@login_required
def view_cart(request):
    cart       = request.session.get('cart', {})
    cart_items = []
    total      = 0

    for item_id, item_data in cart.items():
        subtotal = item_data['Price'] * item_data['quantity']
        cart_items.append({
            'id':       item_id,
            'name':     item_data['Name'],
            'price':    item_data['Price'],
            'quantity': item_data['quantity'],
            'subtotal': subtotal,
            'image':    item_data['Image'],
        })
        total += subtotal
    success_message = request.session.pop('success_message', None)
    error_message = request.session.pop('error_message', None)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total,'success_message': success_message,'error_message': error_message,})


@login_required
def update_cart(request, item_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        try:
            new_quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            new_quantity = 1

        key = str(item_id)
        if key in cart:
            if new_quantity > 0:
                cart[key]['quantity'] = new_quantity
            else:
                del cart[key]
            request.session['cart']  = cart
            request.session.modified = True

    return redirect('view_cart')


@login_required
def delete_cart(request, item_id):
    cart = request.session.get('cart', {})
    key  = str(item_id)
    if key in cart:
        del cart[key]
        request.session['cart']  = cart
        request.session.modified = True
    return redirect('view_cart')


@login_required
def proceed_to_pay(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart:
            request.session['error_message'] = "Your cart is empty."
            return redirect('view_cart')

        user = get_logged_in_user(request)
        created_orders = []

        for item_id, item_data in cart.items():
            try:
                product   = bakery_models.objects.get(id=int(item_id))
                qty       = item_data['quantity']
                total     = product.Price * qty
                new_order = order.objects.create(
                    customer    = user,
                    products    = product,
                    quantity    = qty,
                    total_price = total,
                    status      = 'Pending',
                )
                created_orders.append(new_order)
            except bakery_models.DoesNotExist:
                continue

        if created_orders:
            request.session.pop('cart', None)
            request.session.modified = True

        return render(request, 'payment_success.html', {
            'orders':    created_orders,
            'order_ids': [o.order_id for o in created_orders],
        })

    return redirect('view_cart')


def track_order(request):
    order_obj = None
    error     = None

    if request.method == 'GET' and request.GET.get('order_id'):
        raw_id = request.GET.get('order_id', '').strip().upper()
        try:
            order_obj = order.objects.select_related('customer', 'products').get(order_id=raw_id)
        except order.DoesNotExist:
            error = f'No order found with ID "{raw_id}". Please check and try again.'

    return render(request, 'track_order.html', {'order': order_obj, 'error': error})


def showall(request):
    data6 = bakery_models.objects.all()
    return render(request, "showall.html", {"data6": data6})