from rest_framework import serializers
from main.models import Product, Cart, Order, OrderItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'

    def validate(self, data):
        """
        Check that the quantity is available in stock.
        """
        product = data['product']
        if product.stock < data['quantity']:
            raise serializers.ValidationError("Not enough stock available.")
        return data

    def create(self, validated_data):
        cart_item = Cart(**validated_data)
        cart_item.total_price = cart_item.product.price * cart_item.quantity
        cart_item.save()
        return cart_item

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.total_price = instance.product.price * instance.quantity
        instance.save()
        return instance


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product')
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_id', 'quantity', 'price', 'created_at', 'updated_at']

    def create(self, validated_data):
        order_item = OrderItem(**validated_data)
        order_item.price = order_item.product.price * order_item.quantity
        order_item.save()
        return order_item

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.price = instance.product.price * instance.quantity
        instance.save()
        return instance


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    items_data = OrderItemSerializer(many=True, write_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_date', 'total_price', 'status', 'items', 'items_data', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items_data')
        order = Order.objects.create(**validated_data)
        total_price = 0

        for item_data in items_data:
            item_data['order'] = order
            order_item = OrderItem.objects.create(**item_data)
            total_price += order_item.price * order_item.quantity

        order.total_price = total_price
        order.save()
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items_data', None)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        if items_data:
            instance.items.all().delete()  # Delete old items
            total_price = 0

            for item_data in items_data:
                item_data['order'] = instance
                order_item = OrderItem.objects.create(**item_data)
                total_price += order_item.price * order_item.quantity

            instance.total_price = total_price
            instance.save()

        return instance
