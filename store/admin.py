from django.contrib import admin
from tags.models import TaggedItem
from django.db.models.aggregates import Count
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils.html import format_html, urlencode
from . import models

class InventoryFilter(admin.SimpleListFilter):
    title = 'Stock'
    parameter_name = 'Stock'
    def lookups(self, request, model_admin):
        return [
            ('>10','Low'),('>50','Avgerage'),('<50','Good')
        ]
    
    def queryset(self, request, queryset):
        if self.value() == '>10':
            return queryset.filter(inventory__lt=10)
        elif self.value() == '>50':
            return queryset.filter(inventory__lt=50)
        else:
            return queryset.filter(inventory__gt=51)
       
      
class TagInline(GenericTabularInline):
    model = TaggedItem
    autocomplete_fields = ['tag']

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    search_fields = ['title']
    actions = ['Clear Inventory']
    inlines = [TagInline]
    list_display = ['title','unit_price','inventory_status','collection_title']
    list_per_page = 10
    list_select_related = ['collection']
    list_filter = ['collection','last_update', InventoryFilter]
    def collection_title(self,product):
        return product.collection.title
    @admin.display(ordering='inventory')
    def inventory_status(self,product):
        if product.inventory > 10:
            return 'Low'
        else :
            return 'In-Stock'
    
    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset:QuerySet):
        updated_count = queryset.update(inventory = 0)
        self.message_user(
            request,
            'f{updated_count} Product has been updated.'
        ) 

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name','membership','orders']
    list_editable = ['membership']
    list_per_page = 10
    list_select_related = ['user']
    ordering = ['user__first_name','user__last_name']
    search_fields = ['first_name__istartswith']

    def orders(self,customer):
        url = (
            reverse('admin:store_order_changelist') + '?' + urlencode({
            'customer__id' : str(customer.id)
            }))
        return format_html('<a href = {}>{}</a>',url,customer.orders_count)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(orders_count=Count('order'))

class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    autocomplete_fields = ['product']


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','placed_at','customer','payment_status']
    inlines = [OrderItemInline]
    autocomplete_fields = ['customer']


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','products_count']
    search_fields = ['title']

    def products_count(self,collection):
        url = (reverse('admin:store_product_changelist') + '?' + urlencode({
            'collection__id' : str(collection.id)
            }))
        return format_html('<a href = {}>{}</a>',url,collection.products_count)
        
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count = Count('products'))

