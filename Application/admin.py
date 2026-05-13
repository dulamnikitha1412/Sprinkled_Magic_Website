from django.contrib import admin
from .models import bakery_models,register_model,customer,order

# Register your models here.
class bakery_admin(admin.ModelAdmin):
    list_display=['id','Name','Items','Price','Stock','Image']
    list_display_links=['Items']
    list_filter=['Price']
    list_editable=['Name']
    search_fields=['id']
    ordering=['id']
    
admin.site.register(bakery_models,bakery_admin)
