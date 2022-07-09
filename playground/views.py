from django.shortcuts import render
from django.db.models import Q, F, Value, Func, ExpressionWrapper, DecimalField
from django.db.models.functions import Concat
from django.db.models.aggregates import Count, Min, Max, Avg, Sum
from store.models import Product, OrderItem, Order, Collection, Customer
from decimal import Decimal


def say_hello(request):
    query_set = Product.objects.annotate(Total_sales=Sum(F('orderitem__quantity'))).filter(Total_sales__isnull=False).order_by('-Total_sales')[:5]
    return render(request, 'hello.html', {'name': 'Mohammad', 'products': list(query_set)})

    # for product in Product.objects.all():
    #     print(product)
    # list(query_set)
    # query_set[0]
    # query_set[:5]
    # query_set = Product.objects.filter(unit_price__range=(20, 30))
    # exists = Product.objects.filter(id=0).exists()
    # product = Product.objects.filter(id=0).first()
    # query_set = Product.objects.filter(collection__id__range=(1, 5))
    # query_set = Product.objects.filter(collection__title='Beauty')
    # query_set = Product.objects.filter(title__contains='coffee') startswith endswith
    # query_set = Product.objects.filter(title__icontains='coffee') istartswith iendswith
    # query_set = Product.objects.filter(last_update__year=2021)
    # query_set = Product.objects.filter(description__isnull=True)
    # query_set = Product.objects.filter(unit_price__lt=20, inventory__lt=10)  --> AND
    # query_set = Product.objects.filter(Q(unit_price__lt=20) | ~Q(inventory__lt=10)) -->OR
    # query_set = Product.objects.filter(inventory=F('unit_price'))
    # query_set = Product.objects.order_by('title') -->ASC
    # query_set = Product.objects.order_by('-title') --> DSC
    # query_set = Product.objects.order_by('title').reverse()
    # Product.objects.order_by('unit_price')[0]
    # query_set = Product.objects.earliest('unit_price')
    # query_set = Product.objects.latest('unit_price')
    # query_set = Product.objects.all()[:5] return first 5 objects
    # query_set = Product.objects.values('title', 'id', 'collection__title') --> retrieving the specific columns
    # query_set = Product.objects.values_list('title', 'id', 'collection__featured_product__title')
    # query_set = Product.objects.filter(id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')
    # query_set = Order.objects.order_by('-placed_at').select_related('customer')[:5]
    # query_set = Order.objects.order_by('-placed_at').prefetch_related('orderitem_set__product').select_related('customer')[:5]
    # query_set = Product.objects.aggregate(count=Count('id'), min_price=Min('unit_price'))
    # query_set = OrderItem.objects.filter(product_id=1).aggregate(unit_sold=Sum('quantity'))
    # query_set = Product.objects.filter(collection_id=3).aggregate(
    #     Avg('unit_price'),
    #     Min('unit_price'),
    #     Max('unit_price')
    # )
    # query_set = Customer.objects.annotate(
    #     full_name=Func(F('first_name'), Value(' '), F('last_name'), function='CONCAT')
    # )
    # query_set = Customer.objects.annotate(
    #     full_name=Concat('first_name', Value(' '), 'last_name')
    # )
    # query_set = Customer.objects.annotate(
    #     order_count=Count('order')  # not order_set
    # )

    # query_set = Product.objects.annotate(
    #     discounted_price=(F('unit_price') * Decimal('0.8'), 2)
    # )
    #
    # query_set = Product.objects.annotate(
    #     discounted_price=ExpressionWrapper(F('unit_price') * 0.8)
    # )
    #
    # query_set = Product.objects.annotate(
    #     discounted_price=ExpressionWrapper(F('unit_price') * 0.8, output_field=DecimalField(max_digits=6,
    #                                                                                         decimal_places=2))
    # )

    # query_set = Customer.objects.annotate(order_count=Count('order')).filter(order_count__gt=5)

    # query_set = Customer.objects.annotate(total_paid=Sum(F('order__orderitem__quantity')*F('order__orderitem__unit_price')))  #prefetch_related('order_set__orderitem_set')  --> gives total paid per customer
    # query_set = Customer.objects.aggregate(total_paid=Sum(F('order__orderitem__quantity')*F('order__orderitem__unit_price')))  #prefetch_related('order_set__orderitem_set')  --> gives total paid per customer  -->Total paid in all orders

    # query_set = Customer.objects.annotate(total_paid=Sum(F('order__orderitem__quantity')*F('order__orderitem__unit_price'), filter=Q(order__payment_status='C')))  #prefetch_related('order_set__orderitem_set')  --> gives total paid per customer

    # query_set = Product.objects.annotate(Total_sales=Sum(F('orderitem__quantity'))).filter(Total_sales__isnull=False).order_by('-Total_sales')[:5]

