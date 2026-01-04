"""
URL configuration for sprinkled_Magic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from Application import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.register_view,name='reg'),
    path('login/',views.login_view,name='login'),
    path('base1/',views.base_view,name='base'),
    path('create/',views.create_view,name='c'),
    path('show/',views.showall,name='all'),
    path('fil/<int:id>/',views.filter_view,name='fil'),
    path('update/<int:id>/',views.update_view,name='up'),
    path('delete/<int:id>/',views.delete_view,name='del'),
    path('fili/<str:Name>/', views.fili, name='fili'),
    path('search/', views.search_view, name='search'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.delete_cart, name='delete_cart'),
    path('pay/', views.proceed_to_pay, name='proceed_to_pay'),


    
    

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
