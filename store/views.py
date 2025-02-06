from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser,DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,UpdateModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product,Collection,OrderItem,Review,Cart,CartItem,Customer,Order
from .serializer import ProductSerializer,CollectionSerializer,ReviewSerializer,CartSerializer,CartItemSerializer,AddCartItemSerlializer,UpdateCartItemSerializer,CustomerSerializer,OrderSerializer
from rest_framework import status
from django.db.models.aggregates import Count
from .permissions import IsAdminOrReadOnly
from .filters import ProductFilters


class ProductViewSet(ModelViewSet):
         queryset = Product.objects.all()
         serializer_class = ProductSerializer
         filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
         filterset_class = ProductFilters
         search_fields = ['title','description']
         ordering_fileds = ['unit_price','last_update']
         permission_classes = [IsAdminOrReadOnly]

         def get_serializer_context(self):
                 return {'request': self.request}
        
         def destroy(self, request, *args, **kwargs):
                 if OrderItem.objects.filter(product_id=kwargs['pk']).count()>0:
                        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED) 
                 return super().destroy(request, *args, **kwargs)
        

class CollectionViewSet(ModelViewSet):
         queryset = Collection.objects.annotate(product_count=Count('products')).all()
         serializer_class = CollectionSerializer
         permission_classes = [IsAdminOrReadOnly]
         def get_serializer_context(self):
                return {'request': self.request}
         def destroy(self, request, *args, **kwargs):
                 if OrderItem.objects.filter(product_id=kwargs['pk']).count()>0:
                        return Response(
                                {'Error' : 'This Collection have some iteams so this fuction can not be implemented'},
                                status=status.HTTP_405_METHOD_NOT_ALLOWED )
                 return super().destroy(request, *args, **kwargs)
         

       
class ReviewViewSet(ModelViewSet):
        serializer_class = ReviewSerializer
        
        def get_queryset(self):
                return Review.objects.filter(product_id=self.kwargs['product_pk'])
        
        def get_serializer_context(self):
                return {'product_id':self.kwargs['product_pk']}
        
class CartViewSet(CreateModelMixin,GenericViewSet,DestroyModelMixin,RetrieveModelMixin):
        queryset = Cart.objects.prefetch_related('items__product').all()
        serializer_class = CartSerializer

class CartItemViewSet(ModelViewSet):
        http_method_names = ['get','post','patch','delete']
        
        def get_serializer_class(self):
                if self.request.method == 'POST':
                        return AddCartItemSerlializer
                elif self.request.method == 'PATCH':
                        return UpdateCartItemSerializer 
                else:
                        return CartItemSerializer
                
        def get_serializer_context(self):
                return {'cart_id':self.kwargs['cart_pk']}


        def get_queryset(self):
                return CartItem.objects.filter(cart_id= self.kwargs['cart_pk']).select_related('product')
        
class CustomerViewSet(ModelViewSet):
        queryset = Customer.objects.all()
        serializer_class = CustomerSerializer
        permission_classes = [DjangoModelPermissionsOrAnonReadOnly]

        @action(detail=False,methods=['GET','PUT'],permission_classes=[IsAuthenticated])
        def me(self,request):
                customer,created = Customer.objects.get_or_create(user_id=request.user.id)
                if request.method == 'GET':
                        serializer = self.get_serializer(customer)
                        return Response(serializer.data)
                elif request.method == 'PUT':
                        serializer = self.get_serializer(customer,data=request.data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        return Response(serializer.data)
                
        def get_permissions(self):
                if self.request.method == 'GET':
                        return [AllowAny()]
                return [IsAuthenticated()]


class OrderViewSet(ModelViewSet):
        queryset = Order.objects.all()
        serializer_class = OrderSerializer