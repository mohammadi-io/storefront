from django.contrib import admin, messages
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models


# Register your models here.

# admin.site.register(models.Collection)
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'number_of_products']
    search_fields = ['title']  # set for the search in add form of Product

    @admin.display(ordering='number_of_products')
    def number_of_products(self, collection):  # in this way list_display detects the field
        url = (reverse('admin:store_product_changelist')  # app_model_page generates /admin/store/product/
               + '?'
               # + 'collection_id=' + str(collection.id)
               + urlencode({'collection_id': str(collection.id)})
               )
        return format_html('<a href="{}">{}</a>', url, collection.number_of_products)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            number_of_products=Count('product')
        )

    # @admin.display(ordering='number_of_products')
    # def number_of_products(self, collection):
    #     return models.Product.objects.filter(collection=collection.id).count()  # the problem is that we really don't have the field to sort


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'  # comes after By
    parameter_name = 'inventory'  # in the URL
    Low = 10

    def lookups(self, request, model_admin):  # defines items will appear
        return [
            ('<10', 'Low')  # Low will be show as an option
        ]

    def queryset(self, request, queryset):  # we implement query logic in this function
        if self.value() == '<10':  # since we have only one option we can remove the if
            return queryset.filter(inventory__lt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):  # naming this way is a convention
    actions = ['clear_inventory']
    autocomplete_fields = ['collection']
    # exclude = ['description']  # for creation form
    # fields = ['title']  # for creation form
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_per_page = 10
    list_select_related = ['collection']  # fetch  all collections and prevents extra queries
    prepopulated_fields = {'slug': ['title', 'collection']}
    # readonly_fields = ['title']  # for creation form
    search_fields = ['title']  # for adding OrderItemInline in Order add

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'

    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(request=request,
                          message=f'{updated_count} product(s) were successfully updated.',
                          level=messages.ERROR)


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'number_of_customer_orders']
    list_editable = ['membership']
    list_per_page = 10
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(ordering='number_of_customer_orders')
    def number_of_customer_orders(self, customer):
        url = reverse('admin:store_order_changelist') + '?' + urlencode({'customer_id': str(customer.id)})
        return format_html('<a href="{}">{}</a>', url, customer.number_of_customer_orders)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            number_of_customer_orders=Count('order')
        )


class OrderItemInline(admin.TabularInline):  # we can also use admin.StackedInline
    autocomplete_fields = ['product']
    extra = 0
    # max_num = 10
    min_num = 1
    model = models.OrderItem


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    # fields = ['order_id', 'customer', 'payment_status']
    list_display = ['id', 'placed_at', 'customer']
    list_per_page = 25
