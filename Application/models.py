from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from datetime import datetime

# Create your models here.
class bakery_models(models.Model):
    Name=models.CharField(max_length=50,blank=True,null=True)
    Items=models.CharField(max_length=45,default="Enter.....")
    Price=models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(10),MaxValueValidator(10000)])
    Date=models.DateTimeField(default=datetime.now)
    Image=models.ImageField(upload_to="image/")
    Link=models.URLField(max_length=500,default=True)
    

class register_model(models.Model):
    Username=models.CharField(max_length=45,unique=True)
    Email=models.EmailField(max_length=60,unique=True)
    Password=models.CharField(max_length=180)