from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models.aggregates import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin, \
    UpdateModelMixin
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet
from .filters import ProductFilter
from .models import Cart, CartItem, Collection, Customer, OrderItem, Product, Review
from .pagination import DefaultPagination
from .serializers import CartSerializer, CartItemSerializer, CollectionSerializer, CustomerSerializer, ReviewSerializer, \
    ProductSerializer
from .permissions import IsAdminOrReadOnly

# Create your views here.


class ProductViewSet(ModelViewSet):  # Merge of ProductList & ProductDetail
    # with one class we can list, create, and update Product
    queryset = Product.objects.all()
    # base name generated from this queryset field automatically. if we remove it,we must define basename in urls module
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['collection_id']  # variable name is important
    filterset_class = ProductFilter
    search_fields = ['title', 'description']  # is it not case-sensitive
    ordering_fields = ['unit_price', 'last_update']
    # pagination_class = PageNumberPagination  # we set the page size in settings.py
    pagination_class = DefaultPagination  # we use this to not set page_size globally or supress the warning
    permission_classes = [IsAdminOrReadOnly]

    # def get_queryset(self):  # we use the function since we have a filtering logic on queryset
    #     queryset = Product.objects.all()
    #     collection_id = self.request.query_params.get('collection_id')
    #     # we use function to have access to self. We don't have it in the class
    #     if collection_id is not None:
    #         return queryset.filter(collection_id=collection_id)
    #     return queryset

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        # we mustn't override delete. Otherwise, we will have deleted for the list of items
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'Error': 'Product has dependent order item'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

    # def delete(self, request, pk):
    #     product = get_object_or_404(Product, pk=pk)
    #     if product.orderitem_set.count() > 0:  # check we have dependents children or not
    #         return Response({'Error': 'Product has dependent order item'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    #     product.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


class ProductList(ListCreateAPIView):
    queryset = Product.objects.select_related('collection').all()
    serializer_class = ProductSerializer  # we can use variables instead of functions when we don't have special logic

    # def get_queryset(self):  # we can use this if we want to implement a logic
    #     return Product.objects.select_related('collection').all()
    #
    # def get_serializer_class(self):
    #     return ProductSerializer

    def get_serializer_context(self):
        return {'request': self.request}


# class ProductList(APIView):
#     def get(self, request):
#         queryset = Product.objects.select_related('collection').all()  # prevents 1000 queries for collection
#         serializer = ProductSerializer(queryset, many=True)  # many is True to iterate
#         return Response(serializer.data)  # gives us browsable API
#
#     def post(self, request):
#         serializer = ProductSerializer(data=request.data)  # we want to deserialize the object here
#         serializer.is_valid(raise_exception=True)  # does the all code below with 400 + errors
#         serializer.save()  # save in DB - calls create or update methods of Serializer
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

# @api_view(['GET', 'POST'])
# def product_list(request):  # the request is a instance of Request of Rest
#     if request.method == 'GET':
#         queryset = Product.objects.select_related('collection').all()  # prevents 1000 queries for collection
#         serializer = ProductSerializer(queryset, many=True)  # many is True to iterate
#         return Response(serializer.data)  # gives us browsable API
#     elif request.method == 'POST':
#         serializer = ProductSerializer(data=request.data)  # we want to deserialize the object here
#         serializer.is_valid(raise_exception=True)  # does the all code below with 400 + errors
#         serializer.save()  # save in DB - calls create or update methods of Serializer
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#         # if serializer.is_valid():
#         #     # serializer._validated_data
#         #     return Response('OK')
#         # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitem_set.count() > 0:  # check we have dependents children or not
            return Response({'Error': 'Product has dependent order item'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class ProductDetail(APIView):
#     def get(self, request, id):
#         product = get_object_or_404(Product, pk=id)
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)
#
#     def put(self, request, id):
#         product = get_object_or_404(Product, pk=id)
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#
#     def delete(self, request, id):
#         product = get_object_or_404(Product, pk=id)
#         if product.orderitem_set.count() > 0:  # check we have dependents children or not
#             return Response({'Error': 'Product has dependent order item'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# @api_view(['GET', 'PUT', 'DELETE'])  # PATCH is for update part of data, PUT is for whole
# def product_detail(request, id):
#     product = get_object_or_404(Product, pk=id)  # Object + parameters, shorten our code from the down
#     if request.method == 'GET':
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer = ProductSerializer(product, data=request.data)  # by passing a product we are updating it
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method == 'DELETE':
#         if product.orderitem_set.count() > 0:  # check we have dependents children or not
#             return Response({'Error': 'Product has dependent order item'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#     # try:
#     #     product = Product.objects.get(pk=id)
#     #     serializer = ProductSerializer(product)
#     #     return Response(serializer.data)
#     # except Product.DoesNotExist:
#     #     return Response(status=status.HTTP_404_NOT_FOUND)


# def product_list(request):
#     return HttpResponse('OK')


class CollectionViewSet(ModelViewSet):  # ReadOnlyModelViewSet for only reading not updating
    queryset = Collection.objects.annotate(products_count=Count('product'))
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response(data={'Error': 'There are some products for this collection.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
    # def delete(self, request, pk):
    #     collection = get_object_or_404(
    #         Collection.objects.annotate(products_count=Count('product')), pk=pk)
    #     if collection.product_set.count() > 0:
    #         return Response({'Error': 'There are some products for this collection.'},
    #                         status=status.HTTP_405_METHOD_NOT_ALLOWED)
    #     collection.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionList(ListCreateAPIView):
    queryset = Collection.objects.annotate(products_count=Count('product'))
    serializer_class = CollectionSerializer


#
# @api_view(['GET', 'POST'])
# def collection_list(request):
#     if request.method == 'GET':
#         queryset = Collection.objects.annotate(products_count=Count('product'))
#         # queryset = Collection.objects.prefetch_related('product_set').all()  # the prefetch improves quality very much by less query to the DB
#         serializer = CollectionSerializer(queryset, many=True)
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         collection = CollectionSerializer(data=request.data)
#         collection.is_valid(raise_exception=True)
#         collection.save()
#         return Response(collection.data, status=status.HTTP_201_CREATED)


class CollectionDetail(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.annotate(products_count=Count('product'))
    serializer_class = CollectionSerializer

    def delete(self, request, pk):
        collection = get_object_or_404(
            Collection.objects.annotate(products_count=Count('product')), pk=pk)
        if collection.product_set.count() > 0:
            return Response({'Error': 'There are some products for this collection.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# @api_view(['GET', 'PUT', 'DELETE'])
# def collection_detail(request, id):
#     collection = get_object_or_404(
#         Collection.objects.annotate(products_count=Count('product')), pk=id)  # we can pass a queryset to function
#     if request.method == 'GET':
#         serializer = CollectionSerializer(instance=collection)
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer = CollectionSerializer(collection, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method == 'DELETE':
#         if collection.product_set.count() > 0:
#             return Response({'Error': 'There are some products for this collection.'},
#                             status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        # prevents from loading all reviews which can be unrelated in all products
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):  # by using context we pass the product_id to the serializer
        return {'product_id': self.kwargs['product_pk']}


class CartViewSet(CreateModelMixin,
                  DestroyModelMixin,
                  RetrieveModelMixin,
                  GenericViewSet):  # we have only the creation part
    queryset = Cart.objects.prefetch_related(
        'items__product').all()  # eager loads items + products, prevent extra queries
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')


class CustomerViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    # We can also set permission globally in settings.py
    permission_classes = [IsAuthenticated]  # if any of the permissions fails, then unauthorized

    def get_permissions(self):  # custom permission for each method
        if self.request.method == 'GET':
            return [AllowAny()]  # Pay attention that we return an instance not the class
        return [IsAuthenticated()]

    @action(methods=['GET', 'PUT'], detail=False)  # when the detail is False, it will be available on list
    def me(self, request):
        # This returns a tuple that we unpacked. created==True if the object not exists
        # (customer, created) = Customer.objects.get_or_create(user_id=request.user.id)
        # Above approach has this problem that it cannot create a new customer without of Customer 1o1 relation
        customer = get_object_or_404(klass=Customer, user_id=request.user.id)
        # Auth middleware adds user to the request
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)  # If it is an AnonymousUser user_id = None
            # When we use Response it is returned as a browsable API
        elif request.method == 'PUT':
            #  if we don't put customer as input
            #  we get duplicate key value violates unique constraint "store_customer_user_id_key"
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
