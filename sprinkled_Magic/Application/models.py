from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
import uuid

# Create your models here.
class bakery_models(models.Model):
    Name=models.CharField(max_length=50,blank=True,null=True)
    Items=models.CharField(max_length=45,default="Enter.....")
    Price=models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(10),MaxValueValidator(10000)])
    Stock = models.IntegerField()
    Image=models.ImageField(upload_to="image/")
    

class register_model(models.Model):
    Username=models.CharField(max_length=45,unique=True)
    Email=models.EmailField(max_length=60,unique=True)
    Password=models.CharField(max_length=180)
    is_admin = models.BooleanField(default=False) 
    
    def __str__(self):
        return self.Username

class customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.name


def generate_order_id():
    """Generate a unique order ID in the format SM-XXXXXX"""
    return 'SM-' + uuid.uuid4().hex[:6].upper()

class order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Preparing', 'Preparing'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
    )
    order_id    = models.CharField(max_length=20, default=generate_order_id, unique=True, editable=False)
    customer = models.ForeignKey(register_model, on_delete=models.CASCADE)
    products = models.ForeignKey(bakery_models, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=50, choices=STATUS)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_id}"

    @property
    def status_step(self):
        """Return the step number for the progress tracker (0-indexed)"""
        steps = ['Pending', 'Preparing', 'Out for Delivery', 'Delivered']
        try:
            return steps.index(self.status)
        except ValueError:
            return 0