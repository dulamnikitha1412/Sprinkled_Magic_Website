from django.shortcuts import render,redirect, get_object_or_404
from .models import bakery_models,register_model
from .forms import bakery_forms,register_forms,Login_form
from django.contrib.auth.hashers import make_password,check_password
from django.contrib import messages
from django.db.models import Q

# Create your views here.
def register_view(request):
    if request.method=='POST':
        form=register_forms(request.POST)
        if form.is_valid():
            username=form.cleaned_data['Username']
            email=form.cleaned_data['Email']
            password=form.cleaned_data['Password']
            password_value=make_password(password)

            if register_model.objects.filter(Username=username).exists():
                messages.error(request,"Username already exists.....")
            elif register_model.objects.filter(Email=email).exists():
                messages.error(request,"Email already exists.....")
            else:
                data=register_model(Username=username,Email=email,Password=password_value)
                data.save()
                messages.success(request,"Registration successful.....")
                return redirect('login')
    else:
        form=register_forms()
    return render(request,'register.html',{'form':form})

def login_view(request):
    if request.method=='POST':
        form=Login_form(request.POST)
        if form.is_valid():
            username=form.cleaned_data['username']
            password=form.cleaned_data['password']
            try:
                user=register_model.objects.get(Username=username)
                if check_password(password,user.Password):
                    messages.success(request,"User Login successful...")
                    return redirect('base')
                else:
                    messages.error(request,'Incorrect password')
            except register_model.DoesNotExist:
                messages.error(request,"User does not exist")
    else:
        form=Login_form()
    return render(request,'login.html',{'form':form})


def base_view(request):
    items = bakery_models.objects.all()
    return render(request, 'base.html', {'items': items})


def create_view(request):
    data=bakery_forms()
    if request.method=='POST':
        data=bakery_forms(request.POST,request.FILES)
        if data.is_valid():
            data.save()
            return redirect('base')
    return render(request,'create.html',{'data':data})



def filter_view(request,id):
    data2=bakery_models.objects.get(id=id)
    return render(request,'filter.html',{'data2':data2})



def update_view(request,id):
    data3=bakery_models.objects.get(id=id)
    if request.method=='POST':
        data4=bakery_forms(request.POST,request.FILES,instance=data3)
        if data4.is_valid():
            data4.save()
            return redirect('base')
    else:
        data4=bakery_forms(instance=data3)
    return render(request,'update.html',{'data4':data4})



def delete_view(request,id):
    data5=bakery_models.objects.get(id=id)
    data5.delete()
    return redirect('base')


def fili(request,Name):
    data6=bakery_models.objects.filter(Name=Name)
    return render(request,'filt.html',{'data6':data6})


def search_view(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        results = bakery_models.objects.filter(
            Q(Name__icontains=query) | Q(Items__icontains=query)
        )
        print("Search Query:", query)
        print("Results Count:", results.count())

    return render(request, 'search_results.html', {'results': results, 'query': query})


def add_to_cart(request, item_id):
    if request.method == "POST":
        try:
            item = get_object_or_404(bakery_models, id=item_id)
            quantity = int(request.POST.get('quantity', 1))
            
        
            if quantity <= 0:
                messages.error(request, "Invalid quantity")
                return redirect('base')

            cart = request.session.get('cart', {})
            item_key = str(item_id)
            
            if item_key in cart:
                cart[item_key]['quantity'] += quantity
            else:
                cart[item_key] = {
                    'Name': item.Name,
                    'Price': float(item.Price),  
                    'quantity': quantity,
                    'Image': item.Image.url if item.Image else '',
                }

            request.session['cart'] = cart
            request.session.modified = True  
            messages.success(request, f"Added {quantity} × {item.Name} to cart.")
        except ValueError:
            messages.error(request, "Invalid quantity")
        except Exception as e:
            messages.error(request, "Error adding item to cart")
            
    return redirect('view_cart')

def showall(request):
    data6 = bakery_models.objects.all()  
    return render(request, "show.html", {"data6": data6})


def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for item_id, item_data in cart.items():
        subtotal = item_data['Price'] * item_data['quantity']
        cart_items.append({
            'id': item_id,
            'name': item_data['Name'],
            'price': item_data['Price'],
            'quantity': item_data['quantity'],
            'subtotal': subtotal,
            'image': item_data['Image']
        })
        total += subtotal
    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })


def update_cart(request, item_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        new_quantity = int(request.POST.get('quantity', 1))

        if str(item_id) in cart:
            if new_quantity > 0:
                cart[str(item_id)]['quantity'] = new_quantity
            else:
                del cart[str(item_id)]

            request.session['cart'] = cart

    return redirect('view_cart')


def delete_cart(request, item_id):
    cart = request.session.get('cart', {})

    if str(item_id) in cart:
        del cart[str(item_id)]
        request.session['cart'] = cart  

    return redirect('view_cart')


def proceed_to_pay(request):
    if request.method == 'POST':
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True

        return render(request, 'payment_success.html')
    return redirect('view_cart')
