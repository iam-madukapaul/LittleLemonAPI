from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItems
from django.contrib.auth.models import User

# Serializer for Category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.HyperlinkedModelSerializer):
    category = CategorySerializer(read_only=True)  # Serialize category as a nested object
    category_id = serializers.IntegerField(write_only=True)  # Allow writing `category_id` directly

    class Meta:
        model = MenuItem
        fields = ['id', 'category', 'category_id', 'title', 'price', 'featured', 'url']

    def create(self, validated_data):
        category_id = validated_data.pop('category_id')  # Get category_id
        try:
            category = Category.objects.get(id=category_id)  # Get category by ID
        except Category.DoesNotExist:
            raise serializers.ValidationError(f"Category with id {category_id} does not exist.")
        
        # Create the MenuItem
        menu_item = MenuItem.objects.create(category=category, **validated_data)
        return menu_item


# Serializer for Cart
class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer()  # Nested serializer to display menu item details
    user = serializers.StringRelatedField()  # Display the username instead of ID

    class Meta:
        model = Cart
        fields = '__all__'

# Serializer for OrderItems
class OrderItemsSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItems
        fields = ['menuitem', 'quantity', 'unit_price', 'price']

# Serializer for Order
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    delivery_crew = serializers.StringRelatedField(read_only=True)
    order_items = OrderItemsSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'date', 'total', 'order_items']

    def create(self, validated_data):
        user = self.context['request'].user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            raise serializers.ValidationError("Your cart is empty. Add items before placing an order.")

        # Create order
        order = Order.objects.create(user=user)

        # Move items from cart to order
        for cart_item in cart_items:
            OrderItems.objects.create(
                order=order,
                menuitem=cart_item.menuitem,
                quantity=cart_item.quantity,
                unit_price=cart_item.menuitem.price,
                price=cart_item.quantity * cart_item.menuitem.price,
            )

        # Clear the cart
        cart_items.delete()

        return order

# Serializer for User (for registration, login, etc.)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
