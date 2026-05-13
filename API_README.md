# Sprinkled Magic REST API

## Setup

### 1. Install dependencies
```bash
pip install djangorestframework
```

### 2. Apply migrations
```bash
python manage.py migrate
```

### 3. Run the server
```bash
python manage.py runserver
```

---

## Authentication

The API uses **Token authentication**.

After registering or logging in, you receive a token. Include it in every
subsequent request:

```
Authorization: Token <your_token_here>
```

---

## Response Format

Every response follows the same envelope:

```json
{
  "success": true,
  "message": "...",
  "data": { ... }
}
```

Errors:
```json
{
  "success": false,
  "errors": { "field": ["error message"] }
}
```

---

## Endpoints

### AUTH

#### Register
```
POST /api/auth/register/
```
**Body:**
```json
{
  "username": "nikitha",
  "email": "nikitha@example.com",
  "password": "Secret@123",
  "confirm_password": "Secret@123"
}
```
**Response 201:**
```json
{
  "success": true,
  "message": "Registration successful.",
  "data": {
    "token": "a3f8e2d1c4b5...",
    "user": { "id": 1, "Username": "nikitha", "Email": "nikitha@example.com" }
  }
}
```
Password rules: min 8 chars, uppercase, lowercase, digit, special character.

---

#### Login
```
POST /api/auth/login/
```
**Body:**
```json
{ "username": "nikitha", "password": "Secret@123" }
```
**Response 200:**
```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "token": "a3f8e2d1c4b5...",
    "user": { "id": 1, "Username": "nikitha", "Email": "nikitha@example.com" }
  }
}
```

---

#### Logout
```
POST /api/auth/logout/
Authorization: Token <token>
```
Deletes the token. The same token will return 401 afterwards.

---

#### My Profile
```
GET /api/auth/me/
Authorization: Token <token>
```
**Response 200:**
```json
{
  "success": true,
  "data": { "id": 1, "Username": "nikitha", "Email": "nikitha@example.com" }
}
```

---

### PRODUCTS

#### List all products  (public — no token needed)
```
GET /api/products/
```
**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "Name": "Chocolate Cake",
      "Items": "Cake",
      "Price": "499.00",
      "Stock": 20,
      "image_url": "http://127.0.0.1:8000/media/image/chocolate.jpg"
    }
  ]
}
```

---

#### Get single product  (public)
```
GET /api/products/<id>/
```

---

#### Create product  (admin only)
```
POST /api/products/
Authorization: Token <admin_token>
Content-Type: multipart/form-data
```
**Body fields:** `Name`, `Items`, `Price`, `Stock`, `Image` (file)

---

#### Update product  (admin only)
```
PUT   /api/products/<id>/     ← full replace
PATCH /api/products/<id>/     ← partial update
Authorization: Token <admin_token>
```

---

#### Delete product  (admin only)
```
DELETE /api/products/<id>/
Authorization: Token <admin_token>
```

---

### ORDERS

#### List orders  (authenticated)
```
GET /api/orders/
Authorization: Token <token>
```
Regular users see only their own orders.
Admins see all orders.

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": 5,
      "order_id": "SM-A1B2C3",
      "customer_name": "nikitha",
      "products": { "id": 1, "Name": "Chocolate Cake", "Price": "499.00" },
      "quantity": 2,
      "total_price": "998.00",
      "status": "Pending",
      "created_at": "2026-05-10T10:30:00Z",
      "updated_at": "2026-05-10T10:30:00Z"
    }
  ]
}
```

---

#### Place an order  (authenticated)
```
POST /api/orders/
Authorization: Token <token>
Content-Type: application/json
```
**Body:**
```json
{ "product_id": 1, "quantity": 2 }
```
**Response 201:**
```json
{
  "success": true,
  "message": "Order placed successfully.",
  "data": {
    "order_id": "SM-A1B2C3",
    "status": "Pending",
    "total_price": "998.00",
    ...
  }
}
```
Returns 400 if stock is insufficient.

---

#### Get order detail  (authenticated)
```
GET /api/orders/SM-A1B2C3/
Authorization: Token <token>
```
Non-admins can only view their own orders (403 otherwise).

---

#### Update order status  (admin only)
```
PATCH /api/orders/SM-A1B2C3/status/
Authorization: Token <admin_token>
Content-Type: application/json
```
**Body:**
```json
{ "status": "Preparing" }
```
Valid statuses: `Pending`, `Preparing`, `Out for Delivery`, `Delivered`

---

## Quick Test with curl

```bash
# 1. Register
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"Test@1234","confirm_password":"Test@1234"}'

# 2. Login → copy the token
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"Test@1234"}'

# 3. List products (no token needed)
curl http://127.0.0.1:8000/api/products/

# 4. Place order (use token from step 2)
curl -X POST http://127.0.0.1:8000/api/orders/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":1}'

# 5. Track order
curl http://127.0.0.1:8000/api/orders/SM-XXXXXX/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

---

## Making a User an Admin

In the Django shell:
```bash
python manage.py shell
```
```python
from Application.models import register_model
user = register_model.objects.get(Username='nikitha')
user.is_admin = True
user.save()
```
