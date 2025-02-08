from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MenuItemViewSet, CartView, OrderView, SingleOrderView, SingleMenuItemView, ManagerUserManagementView, SingleManagerUserView, DeliveryCrewUserManagementView, SingleDeliveryCrewUserView

router = DefaultRouter()
router.register(r'menu-items', MenuItemViewSet)

urlpatterns = [
    path('cart/menu-items', CartView.as_view(), name='cart-menu-items'),
    path('orders/', OrderView.as_view(), name='orders-list'),
    path('orders/<int:order_id>', SingleOrderView.as_view(), name='single-order'),
    path('', include(router.urls)),  # Include router for menu items
    path('menu-items/<int:pk>', SingleMenuItemView.as_view(), name='single-menu-item'),
    path('groups/manager/users', ManagerUserManagementView.as_view(), name='manager-users'),
    path('groups/manager/users/<str:username>', SingleManagerUserView.as_view(), name='single-manager-user'),
    path('groups/delivery-crew/users', DeliveryCrewUserManagementView.as_view(), name='delivery-crew-users'),
    path('groups/delivery-crew/users/<str:username>', SingleDeliveryCrewUserView.as_view(), name='single-delivery-crew-user'),
]
