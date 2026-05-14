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
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from Application import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Application.urls')),
    path('',views.register_view,name='reg'),
    path('login/',views.login_view,name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('base1/',views.base_view,name='base'),
    path('create/',views.create_view,name='create'),
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
    path('about/', views.about, name='about'),
    path('reviews/', views.reviews, name='reviews'),
    path('contact/', views.contact, name='contact'),
    path('careers/', views.careers, name='careers'),
    path('customize-cake/', views.customize_cake, name='customize_cake'),
    path('custom-gifts/', views.custom_gifts, name='custom_gifts'),
    path('corporate-orders/', views.corporate_orders, name='corporate_orders'),
    path('support/', views.support, name='support'),
    path('faqs/', views.faqs, name='faqs'),
    path('shipping-delivery/', views.shipping_delivery, name='shipping_delivery'),
    path('return-policy/', views.return_policy, name='return_policy'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-condition/', views.terms_condition, name='terms_condition'),
    path('blog/', views.blog, name='blog'),
    path('gifts-to-mother/', views.gifts_to_mother, name='gifts_to_mother'),
    path('birthday-cakes/', views.birthday_cakes, name='birthday_cakes'),
    path('anniversary-cakes/', views.anniversary_cakes, name='anniversary_cakes'),
    path('first-anniversary-gifts/', views.first_anniversary_gifts, name='first_anniversary_gifts'),
    path('twentyfive-anniversary-gifts/', views.twentyfive_anniversary_gifts, name='twentyfive_anniversary_gifts'),
    path('baby-boy-cakes/', views.baby_boy_cakes, name='baby_boy_cakes'),
    path('baby-girl-cakes/', views.baby_girl_cakes, name='baby_girl_cakes'),
    path('mothers-day-gifts/', views.mothers_day_gifts, name='mothers_day_gifts'),
    path('parents-day-gifts/', views.parents_day_gifts, name='parents_day_gifts'),
    path('friendship-day-gifts/', views.friendship_day_gifts, name='friendship_day_gifts'),
    path('rakhi-gifts/', views.rakhi_gifts, name='rakhi_gifts'),
    path('christmas-gifts/', views.christmas_gifts, name='christmas_gifts'),
    path('new-year-gifts/', views.new_year_gifts, name='new_year_gifts'),
    path('valentines-day-gifts/', views.valentines_day_gifts, name='valentines_day_gifts'),


    
    

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
