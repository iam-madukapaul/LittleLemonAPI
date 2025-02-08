from rest_framework import viewsets, status, generics, filters, serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .models import MenuItem, Cart, Order, OrderItems
from .serializers import MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemsSerializer
from django.contrib.auth.models import User, Group
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound

# Custom permission to allow only managers to modify menu items
class IsManager(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True  # Allow everyone to view menu items
        return request.user.groups.filter(name='Manager').exists()  # Only managers can modify

# ViewSet for MenuItem (Managers only for modifications)
class MenuItemViewSet(viewsets.ModelViewSet):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManager]
    
    # Enable search, ordering, and filtering 
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter] 
    
    # Define fields to filter by 
    filterset_fields = ['title', 'price',] # Fields for DjangoFilterBackend 
    
    # Define search fields 
    search_fields = ['title', 'category__title'] # Fields for SearchFilter 
    
    # Define ordering fields 
    ordering_fields = ['title', 'price',] # Fields for OrderingFilter 
    # ordering = ['-created_at'] # Default ordering

    def perform_create(self, serializer):
        serializer.save()

# View for a single menu item
class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManager]
    

class ManagerUserManagementView(APIView):
    permission_classes = [IsAdminUser]  # Only Admins can manage managers

    def get(self, request):
        """List all users in the 'Manager' group."""
        try:
            manager_group = Group.objects.get(name='Manager')
            managers = manager_group.user_set.all()
            return Response({"managers": [user.username for user in managers]})
        except Group.DoesNotExist:
            return Response({"error": "Manager group does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Add a user to the 'Manager' group using username."""
        username = request.data.get("username")
        if not username:
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(username=username)
            manager_group, created = Group.objects.get_or_create(name='Manager')
            user.groups.add(manager_group)
            return Response({"message": f"User {user.username} added to Manager group."}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class SingleManagerUserView(APIView):
    permission_classes = [IsAdminUser]  # Only Admins can remove managers

    def delete(self, request, username):
        """Remove a user from the 'Manager' group using username."""
        try:
            user = User.objects.get(username=username)
            manager_group = Group.objects.get(name='Manager')
            user.groups.remove(manager_group)
            return Response({"message": f"User {user.username} removed from Manager group."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"error": "Manager group does not exist"}, status=status.HTTP_404_NOT_FOUND)
        

# Custom permission to allow only Managers
class IsManagerPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="Manager").exists()

class DeliveryCrewUserManagementView(APIView):
    permission_classes = [IsManagerPermission]  # Only managers can manage delivery crew

    def get(self, request):
        """List all users in the 'Delivery Crew' group."""
        try:
            delivery_group = Group.objects.get(name='Delivery Crew')
            delivery_crew = delivery_group.user_set.all()
            return Response({"delivery_crew": [user.username for user in delivery_crew]})
        except Group.DoesNotExist:
            return Response({"error": "Delivery Crew group does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Add a user to the 'Delivery Crew' group using username."""
        username = request.data.get("username")
        if not username:
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(username=username)
            delivery_group, created = Group.objects.get_or_create(name='Delivery Crew')
            user.groups.add(delivery_group)
            return Response({"message": f"User {user.username} added to Delivery Crew group."}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class SingleDeliveryCrewUserView(APIView):
    permission_classes = [IsManagerPermission]  # Only managers can remove delivery crew members

    def delete(self, request, username):
        """Remove a user from the 'Delivery Crew' group using username."""
        try:
            user = User.objects.get(username=username)
            delivery_group = Group.objects.get(name='Delivery Crew')
            user.groups.remove(delivery_group)
            return Response({"message": f"User {user.username} removed from Delivery Crew group."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"error": "Delivery Crew group does not exist"}, status=status.HTTP_404_NOT_FOUND)


# View for Cart Management (Customers only)
class CartView(APIView):
    permission_classes = [IsAuthenticated]  # Only logged-in users can access

    def get(self, request):
        """Return all cart items for the authenticated user"""
        cart_items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(cart_items, many=True, context={'request': request})  #Pass request context
        return Response(serializer.data)

    def post(self, request):
        """Add a menu item to the cart or update quantity"""
        menu_item_id = request.data.get("menuitem")
        quantity = int(request.data.get("quantity", 1))  # Default to 1 if not provided
        
        if not menu_item_id or not quantity or int(quantity) <= 0:
            return Response({"error": "Invalid menu item or quantity"}, status=status.HTTP_400_BAD_REQUEST)

        menu_item_obj = get_object_or_404(MenuItem, id=menu_item_id)

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            menuitem=menu_item_obj,
            defaults={'quantity': quantity}  # No need to set unit_price, handled in model
        )
        

        if not created:
            cart_item.quantity = quantity  # Update quantity # Instead of adding +=, we set the new quantity
        cart_item.save()  # Triggers the `save()` method in the model

        return Response(CartSerializer(cart_item, context={'request': request}).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        """Remove all cart items for the authenticated user"""
        Cart.objects.filter(user=request.user).delete()
        return Response({"message": "Cart cleared successfully"}, status=status.HTTP_204_NO_CONTENT)

# View for Order Management (Customers, Managers, Delivery Crew)
class OrderView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    # Enable search, ordering, and filtering
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]

    # Define fields to filter by
    filterset_fields = ['user__username', 'delivery_crew__username', 'status']

    # Define search fields - Adjust to correctly refer to the fields in related models
    search_fields = ['user__username', 'delivery_crew__username']  # Corrected this to use `delivery_crew__username`

    # Define ordering fields
    ordering_fields = ['user__username', 'status']

    def get_queryset(self):
        """
        Return different sets of orders based on the user's role.
        """
        if self.request.user.groups.filter(name="Manager").exists():
            # Manager sees all orders
            return Order.objects.all()
        elif self.request.user.groups.filter(name="Delivery Crew").exists():
            # Delivery crew sees only their assigned orders
            return Order.objects.filter(delivery_crew=self.request.user)
        else:
            # Customers see only their own orders
            return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Create an order from the current cart items and clear the cart.
        """
        user = self.request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            raise serializers.ValidationError("Your cart is empty. Add items before placing an order.")

        # Create the order
        order = Order.objects.create(user=user, total=0, date=timezone.now())

        total_price = 0  # Track total order price

        # Move items from cart to order
        for cart_item in cart_items:
            order_item = OrderItems.objects.create(
                order=order,
                menuitem=cart_item.menuitem,
                quantity=cart_item.quantity,
                unit_price=cart_item.menuitem.price,
                price=cart_item.quantity * cart_item.menuitem.price,
            )
            total_price += order_item.price  # Add price to total

        # Update order total
        order.total = total_price
        order.save()

        # Clear the cart after creating the order
        cart_items.delete()

        return order



class SingleOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, order_id):
        try:
            return Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise NotFound("Order not found")

    def get(self, request, order_id):
        order = self.get_object(order_id)

        if request.user.groups.filter(name="Manager").exists() or \
           request.user == order.user or \
           request.user == order.delivery_crew:
            serializer = OrderSerializer(order, context={'request': request})
            return Response(serializer.data)

        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Manager: Assign delivery crew and update status
        if request.user.groups.filter(name="Manager").exists():
            delivery_crew_username = request.data.get('delivery_crew')
            if delivery_crew_username:
                try:
                    delivery_crew = User.objects.get(username=delivery_crew_username)
                    order.delivery_crew = delivery_crew
                except User.DoesNotExist:
                    return Response({"error": "Delivery crew user not found"}, status=status.HTTP_400_BAD_REQUEST)

            order.status = request.data.get('status', order.status)  # Keep the current status if not provided
            order.save()
            return Response(OrderSerializer(order, context={'request': request}).data)

        # Delivery Crew: Only allowed to update status
        if request.user.groups.filter(name="Delivery Crew").exists():
            if "status" in request.data:
                order.status = request.data['status']
                order.save()
                return Response(OrderSerializer(order, context={'request': request}).data)
            return Response({"error": "You can only update the status."}, status=status.HTTP_403_FORBIDDEN)

        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)


    def delete(self, request, order_id):
        if request.user.groups.filter(name="Manager").exists():
            order = self.get_object(order_id)
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)



