from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from main.permissions import IsAdminOrReadOnly
from main.models import Product, Cart, Order, OrderItem
from main.serializers import ProductSerializer, CartSerializer, OrderSerializer, OrderItemSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAdminOrReadOnly]

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure that users can only see their own cart items
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically associate the logged-in user with the cart item
        serializer.save(user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure that users can only see their own orders
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically associate the logged-in user with the order
        serializer.save(user=self.request.user)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure that users can only see their order items through their orders
        return self.queryset.filter(order__user=self.request.user)
