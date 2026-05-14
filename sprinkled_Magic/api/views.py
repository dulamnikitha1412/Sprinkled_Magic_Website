"""
REST API views for Sprinkled Magic.

Auth endpoints
--------------
POST /api/auth/register/     → create account, returns token
POST /api/auth/login/        → returns token
POST /api/auth/logout/       → deletes token
GET  /api/auth/me/           → current user profile

Product endpoints
-----------------
GET    /api/products/        → list all products
GET    /api/products/<id>/   → single product
POST   /api/products/        → create  (admin only)
PUT    /api/products/<id>/   → full update (admin only)
PATCH  /api/products/<id>/   → partial update (admin only)
DELETE /api/products/<id>/   → delete (admin only)

Order endpoints
---------------
GET  /api/orders/            → list caller's orders (admin sees all)
POST /api/orders/            → place order (authenticated)
GET  /api/orders/<order_id>/ → order detail
PATCH /api/orders/<order_id>/status/ → update status (admin only)
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from Application.models import bakery_models, register_model, order
from .authentication import TokenAuthentication, ApiToken
from .permissions import IsAuthenticated, IsAdminUser
from .serializers import (
    ProductSerializer,
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusSerializer,
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def api_response(data=None, message=None, errors=None, status_code=200):
    """Consistent envelope for every response."""
    body = {'success': errors is None}
    if message:
        body['message'] = message
    if data is not None:
        body['data'] = data
    if errors is not None:
        body['errors'] = errors
    return Response(body, status=status_code)


# ===========================================================================
# AUTH VIEWS
# ===========================================================================

class RegisterView(APIView):
    """
    POST /api/auth/register/

    Body: { username, email, password, confirm_password }
    Returns: { token, user }
    """
    authentication_classes = []
    permission_classes     = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(errors=serializer.errors,
                                status_code=status.HTTP_400_BAD_REQUEST)

        user  = serializer.save()
        token = ApiToken.get_or_create_for(user)
        return api_response(
            data    = {'token': token, 'user': UserSerializer(user).data},
            message = "Registration successful.",
            status_code = status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/auth/login/

    Body: { username, password }
    Returns: { token, user }
    """
    authentication_classes = []
    permission_classes     = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(errors=serializer.errors,
                                status_code=status.HTTP_400_BAD_REQUEST)

        user  = serializer.validated_data['user']
        token = ApiToken.get_or_create_for(user)
        return api_response(
            data    = {'token': token, 'user': UserSerializer(user).data},
            message = "Login successful.",
        )


class LogoutView(APIView):
    """
    POST /api/auth/logout/

    Deletes the caller's token.  Subsequent requests with the same token
    will receive 401.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.api_token.delete()
        except ApiToken.DoesNotExist:
            pass
        return api_response(message="Logged out successfully.")


class MeView(APIView):
    """
    GET /api/auth/me/

    Returns the authenticated user's profile.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated]

    def get(self, request):
        return api_response(data=UserSerializer(request.user).data)


# ===========================================================================
# PRODUCT VIEWS
# ===========================================================================

class ProductListView(APIView):
    """
    GET  /api/products/   → list all products (public)
    POST /api/products/   → create product   (admin only)
    """
    authentication_classes = [TokenAuthentication]
    permission_classes     = []  # GET is public; POST checked inside

    def get(self, request):
        products   = bakery_models.objects.all().order_by('id')
        serializer = ProductSerializer(products, many=True,
                                       context={'request': request})
        return api_response(data=serializer.data)

    def post(self, request):
        # Manually enforce admin permission for writes
        auth = TokenAuthentication()
        result = auth.authenticate(request)
        if not result:
            return api_response(errors="Authentication required.",
                                status_code=status.HTTP_401_UNAUTHORIZED)
        user, _ = result
        if not getattr(user, 'is_admin', False):
            return api_response(errors="Admin access required.",
                                status_code=status.HTTP_403_FORBIDDEN)

        serializer = ProductSerializer(data=request.data,
                                       context={'request': request})
        if not serializer.is_valid():
            return api_response(errors=serializer.errors,
                                status_code=status.HTTP_400_BAD_REQUEST)
        product = serializer.save()
        return api_response(
            data        = ProductSerializer(product, context={'request': request}).data,
            message     = "Product created.",
            status_code = status.HTTP_201_CREATED,
        )


class ProductDetailView(APIView):
    """
    GET    /api/products/<id>/   → public
    PUT    /api/products/<id>/   → admin only
    PATCH  /api/products/<id>/   → admin only
    DELETE /api/products/<id>/   → admin only
    """
    authentication_classes = [TokenAuthentication]
    permission_classes     = []

    def _get_product(self, pk):
        return get_object_or_404(bakery_models, pk=pk)

    def _require_admin(self, request):
        result = TokenAuthentication().authenticate(request)
        if not result:
            return None, api_response(errors="Authentication required.",
                                      status_code=status.HTTP_401_UNAUTHORIZED)
        user, _ = result
        if not getattr(user, 'is_admin', False):
            return None, api_response(errors="Admin access required.",
                                      status_code=status.HTTP_403_FORBIDDEN)
        return user, None

    def get(self, request, pk):
        product    = self._get_product(pk)
        serializer = ProductSerializer(product, context={'request': request})
        return api_response(data=serializer.data)

    def put(self, request, pk):
        _, err = self._require_admin(request)
        if err:
            return err
        product    = self._get_product(pk)
        serializer = ProductSerializer(product, data=request.data,
                                       context={'request': request})
        if not serializer.is_valid():
            return api_response(errors=serializer.errors,
                                status_code=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return api_response(data=serializer.data, message="Product updated.")

    def patch(self, request, pk):
        _, err = self._require_admin(request)
        if err:
            return err
        product    = self._get_product(pk)
        serializer = ProductSerializer(product, data=request.data, partial=True,
                                       context={'request': request})
        if not serializer.is_valid():
            return api_response(errors=serializer.errors,
                                status_code=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return api_response(data=serializer.data, message="Product updated.")

    def delete(self, request, pk):
        _, err = self._require_admin(request)
        if err:
            return err
        product = self._get_product(pk)
        product.delete()
        return api_response(message=f"Product {pk} deleted.",
                            status_code=status.HTTP_200_OK)


# ===========================================================================
# ORDER VIEWS
# ===========================================================================

class OrderListView(APIView):
    """
    GET  /api/orders/   → authenticated user's own orders
                          (admin sees all orders)
    POST /api/orders/   → place a new order (authenticated)
    """
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if getattr(user, 'is_admin', False):
            orders = order.objects.select_related('customer', 'products') \
                                  .order_by('-created_at')
        else:
            orders = order.objects.filter(customer=user) \
                                  .select_related('customer', 'products') \
                                  .order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return api_response(data=serializer.data)

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(errors=serializer.errors,
                                status_code=status.HTTP_400_BAD_REQUEST)

        product  = bakery_models.objects.get(pk=serializer.validated_data['product_id'])
        quantity = serializer.validated_data['quantity']
        total    = product.Price * quantity

        new_order = order.objects.create(
            customer    = request.user,
            products    = product,
            quantity    = quantity,
            total_price = total,
            status      = 'Pending',
        )
        return api_response(
            data        = OrderSerializer(new_order).data,
            message     = "Order placed successfully.",
            status_code = status.HTTP_201_CREATED,
        )


class OrderDetailView(APIView):
    """
    GET /api/orders/<order_id>/

    Authenticated users can only view their own orders.
    Admins can view any order.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated]

    def get(self, request, order_id):
        order_obj = get_object_or_404(
            order.objects.select_related('customer', 'products'),
            order_id=order_id.upper(),
        )
        # Non-admins can only see their own orders
        if not getattr(request.user, 'is_admin', False):
            if order_obj.customer_id != request.user.pk:
                return api_response(
                    errors="You do not have permission to view this order.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        return api_response(data=OrderSerializer(order_obj).data)


class OrderStatusView(APIView):
    """
    PATCH /api/orders/<order_id>/status/

    Admin-only: update order status.
    Body: { "status": "Preparing" }
    """
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated, IsAdminUser]

    def patch(self, request, order_id):
        order_obj  = get_object_or_404(order, order_id=order_id.upper())
        serializer = OrderStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(errors=serializer.errors,
                                status_code=status.HTTP_400_BAD_REQUEST)
        order_obj.status = serializer.validated_data['status']
        order_obj.save()
        return api_response(
            data    = OrderSerializer(order_obj).data,
            message = f"Order {order_id} status updated to '{order_obj.status}'.",
        )
