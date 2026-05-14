"""
Serializers for the Sprinkled Magic REST API.

Products  → ProductSerializer
Orders    → OrderSerializer, OrderCreateSerializer
Auth      → RegisterSerializer, LoginSerializer, TokenSerializer
"""

import re
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import serializers

from Application.models import bakery_models, register_model, order


class ProductSerializer(serializers.ModelSerializer):
    """Full read/write serializer for bakery products."""

    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = bakery_models
        fields = ['id', 'Name', 'Items', 'Price', 'Stock', 'Image', 'image_url']
        extra_kwargs = {
            'Image': {'required': False, 'write_only': True},
        }

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.Image and request:
            return request.build_absolute_uri(obj.Image.url)
        return None

    def validate_Price(self, value):
        if value < 10 or value > 10000:
            raise serializers.ValidationError("Price must be between ₹10 and ₹10,000.")
        return value

    def validate_Stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value



class OrderProductSerializer(serializers.ModelSerializer):
    """Lightweight product info nested inside order responses."""
    class Meta:
        model  = bakery_models
        fields = ['id', 'Name', 'Price']


class OrderSerializer(serializers.ModelSerializer):
    """Full order representation returned in responses."""
    products       = OrderProductSerializer(read_only=True)
    customer_name  = serializers.CharField(source='customer.Username', read_only=True)

    class Meta:
        model  = order
        fields = [
            'id', 'order_id', 'customer_name',
            'products', 'quantity', 'total_price',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'order_id', 'total_price', 'created_at', 'updated_at',
        ]


class OrderCreateSerializer(serializers.Serializer):
    """Validates the payload when a customer places an order."""
    product_id = serializers.IntegerField()
    quantity   = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        try:
            bakery_models.objects.get(pk=value)
        except bakery_models.DoesNotExist:
            raise serializers.ValidationError(f"No product with id {value}.")
        return value

    def validate(self, attrs):
        product  = bakery_models.objects.get(pk=attrs['product_id'])
        quantity = attrs['quantity']
        if product.Stock < quantity:
            raise serializers.ValidationError(
                f"Only {product.Stock} unit(s) in stock for '{product.Name}'."
            )
        return attrs


class OrderStatusSerializer(serializers.Serializer):
    """Used by admins to update an order's status."""
    VALID = [c[0] for c in order.STATUS]
    status = serializers.ChoiceField(choices=VALID)




class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    confirm_password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'confirm_password'
        ]

    def validate_username(self, value):

        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "Username already taken."
            )

        return value

    
    def validate_email(self, value):

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Email already registered."
            )

        return value

    
    def validate_password(self, value):

        errors = []

        if len(value) < 8:
            errors.append("at least 8 characters")

        if not re.search(r'[A-Z]', value):
            errors.append("an uppercase letter")

        if not re.search(r'[a-z]', value):
            errors.append("a lowercase letter")

        if not re.search(r'\d', value):
            errors.append("a digit")

        if not re.search(r'[^A-Za-z0-9]', value):
            errors.append("a special character")

        if errors:
            raise serializers.ValidationError(
                f"Password must contain: {', '.join(errors)}."
            )

        return value

    
    def validate(self, attrs):

        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        return attrs

    
    def create(self, validated_data):

        validated_data.pop('confirm_password')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError(
                "Username and password are required."
            )
        user = authenticate(
            username=username,
            password=password
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid username or password."
            )
        if not user.is_active:
            raise serializers.ValidationError(
                "Account is disabled."
            )
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Safe public representation of a user (no password)."""
    class Meta:
        model  = register_model
        fields = ['id', 'Username', 'Email']
