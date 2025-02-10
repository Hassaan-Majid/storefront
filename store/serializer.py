from  rest_framework import serializers
from .models import Product,Collection,Review,Cart,CartItem,Customer,Order,OrderItem
from decimal import Decimal

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','inventory','description','slug','unit_price','price_with_tax','collection']
        
    price_with_tax = serializers.SerializerMethodField(method_name= 'calculate')

    def calculate (self, product:Product):
        return product.unit_price * Decimal(1.1)


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id','title','product_count']
    
    product_count = serializers.IntegerField(read_only=True)


class ReviewSerializer(serializers.ModelSerializer):
     class Meta:
         model = Review
         fields = ['id','name','description','date']

     def create(self, validated_data):
         product_id = self.context['product_id']
         return Review.objects.create(product_id=product_id,**validated_data)

class BasicProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    product = BasicProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self,cart_item:CartItem):
        return cart_item.quantity * cart_item.product.unit_price
    
    class Meta:
        model = CartItem
        fields = ['id','product','quantity','total_price']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only = True)
    items = CartItemSerializer(many=True,read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price (self, cart):
        return sum([item.quantity*item.product.unit_price for item in cart.items.all()])
    class Meta:
        model = Cart
        fields = ['id','items','total_price']


class AddCartItemSerlializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    
    def validate_product_id(self,value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Product not found')
        return value
            

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        try :
            cart_item =CartItem.objects.get(cart_id=cart_id,product_id=product_id) 
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
           self.instance = CartItem.objects.create(cart_id=cart_id,**self.validated_data)
           return self.instance

    class Meta:
        model = CartItem
        fields = ['id','product_id','quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Customer
        fields = ['id','phone','user_id','membership','birth_date']
    

class OrderItemSerializer(serializers.ModelSerializer):
        product = BasicProductSerializer()
        class Meta:
                model = OrderItem
                fields = ['id','product','unit_price','quantity']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)
    class Meta:
        model = Order 
        fields = ['id','placed_at','payment_status','customer','order_items']

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def save(self, **kwargs):
        print(self.validated_data['cart_id'])
        print(self.context['user_id'])