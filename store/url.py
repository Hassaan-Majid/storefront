from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('products',views.ProductViewSet)
router.register('collections',views.CollectionViewSet)
router.register('carts',views.CartViewSet)
router.register('customer',views.CustomerViewSet)
router.register('order',views.OrderViewSet)

product_router = routers.NestedDefaultRouter(router,'products',lookup= 'product')
product_router.register('reviews',views.ReviewViewSet,basename='product-reviews')

cart_router = routers.NestedDefaultRouter(router,'carts',lookup='cart')
cart_router.register('items',views.CartItemViewSet,basename='cart-items')

urlpatterns = router.urls + product_router.urls + cart_router.urls