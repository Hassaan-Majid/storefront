from django.shortcuts import render
from django.http import HttpResponse
from django.db.models.aggregates import Min,Max,Count,Avg,Sum
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from store.models import Product,OrderItem,Order
from tags.models import TaggedItem


def say_hello(request):
    # try:
    #     #qset = Product.objects.filter(id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')
    #     # qset = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]
    # except ObjectDoesNotExist:
    #     pass
    TaggedItem.objects.get_tag_for(Product,1)
    return render(request, 'hello.html', {'name': 'Mosh','result':'qset'})
