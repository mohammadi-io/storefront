from decimal import Decimal
from .models import Cart, CartItem, Collection, Customer, Review, Product
from rest_framework import serializers


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.IntegerField(read_only=True)  # we define it here to prevent error
    # read only is important so it won't be required to be given and inserted to db

    # products_count = serializers.SerializerMethodField(method_name='number_of_products')
    #
    # def number_of_products(self, collection: Collection):
    #     return collection.product_set.count()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price', 'inventory', 'price_with_tax', 'collection', 'slug', 'description']

    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)  # important for receiving data
    # price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')  # we set the source when
    # # it mismatches the name
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

    # collection = CollectionSerialzer()  # creates nested object

    # collection = serializers.HyperlinkedRelatedField()  # for hyperlink

    # collection = serializers.StringRelatedField()  # string representation

    # collection = serializers.PrimaryKeyRelatedField(
    #     queryset=Collection.objects.all()   # apply the search on this queryset
    # )

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)

    # def validate(self, data):  # custom validation method
    #     if data['password'] != data['confirm_password']:
    #         return serializers.ValidationError('Passwords don\'t match')
    #     return data
    #


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'product', 'name', 'description', 'date']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)


class SimpleProductSerializer(serializers.ModelSerializer):  # This is the serializer we use in carts showing
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price', 'slug']

    title = serializers.CharField(max_length=255, read_only=True)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    slug = serializers.SlugField(read_only=True)


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity', 'total_price']

    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    product = SimpleProductSerializer()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'items', 'total_price']

    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    items = CartItemSerializer(many=True, read_only=True)  # This name should be like related_name in the model def
    created_at = serializers.DateTimeField(read_only=True)

    def get_total_price(self, cart: Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])
        # total = 0
        # cart_items = CartItem.objects.filter(cart_id=cart.id)
        # for cart_item in cart_items:
        #     total += cart_item.quantity * cart_item.product.unit_price
        # return total


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']
