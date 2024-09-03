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
        product = data.get('product')
        if product.stock < data.get('quantity'):
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
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'

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
    items = OrderItemSerializer(many=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        total_price = 0

        for item_data in items_data:
            item_data['order'] = order
            order_item = OrderItem.objects.create(**item_data)
            total_price += order_item.price

        order.total_price = total_price
        order.save()
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        if items_data:
            instance.items.all().delete()  # Delete old items
            total_price = 0

            for item_data in items_data:
                item_data['order'] = instance
                order_item = OrderItem.objects.create(**item_data)
                total_price += order_item.price

            instance.total_price = total_price
            instance.save()

        return instance
