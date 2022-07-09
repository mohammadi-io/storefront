from django.urls import path
from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework_nested import routers
from . import views
from pprint import pprint

router = routers.DefaultRouter()  # generates Api Root + Model.json for Json String
router.register(prefix='products', viewset=views.ProductViewSet, basename='products')
router.register(prefix='collections', viewset=views.CollectionViewSet)
router.register(prefix='carts', viewset=views.CartViewSet)
router.register(prefix='customers', viewset=views.CustomerViewSet)
# pprint(router.urls)
products_router = routers.NestedDefaultRouter(parent_router=router, parent_prefix='products', lookup='product')  # the lookup means we will have product_pk as a parameter
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')
# pprint(products_router.urls)
cart_items_router = routers.NestedDefaultRouter(parent_router=router, parent_prefix='carts', lookup='cart')
cart_items_router.register(prefix='cartitems', viewset=views.CartItemViewSet, basename='cart-items')

# URLConf
urlpatterns = router.urls + products_router.urls + cart_items_router.urls
# [
#     path('products/', views.ProductList.as_view()),
#     path('products/<int:pk>/', views.ProductDetail.as_view()),
#     path('collections/', views.CollectionList.as_view()),
#     path('collections/<int:pk>/', views.CollectionDetail.as_view())
# ]
