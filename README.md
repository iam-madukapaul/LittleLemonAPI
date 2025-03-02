A Django REST framework API for managing menu items, orders, carts, and delivery operations at the Little Lemon restaurant. 
This API enables role-based access for Managers, Delivery Crew, and Customers to manage and track menu items, place and manage orders, and assign delivery crews to orders in real-time.

**Features**

- User roles: Manager, Delivery Crew, and Customers
- JWT Authentication with Djoser
- Menu Management (CRUD operations)
- Cart and Order Processing
- Role-Based Access Control

**Installation**

1. Clone the repository:
   git clone https://github.com/iam-madukapaul/LittleLemonAPI.git
   cd LittleLemonAPI

2. Create a virtual environment and install dependencies:
   pipenv install
   pipenv shell

3. Apply migrations:
   python manage.py migrate

4. Create a superuser:
   python manage.py createsuperuser

5. Run the development server:
   python manage.py runserver

**API Endpoints**

A. User registration and tokaen generation endpoint
1. POST /api/users - Creates a new user
2. GET /api/users/me - Display only the current user
3. POST /api/token/login - Generates access tokens
   
B. Menu-items endpoints
1. GET /api/menu-items - List all menu items (public)
2. POST /api/menu-items/ - Add new menu items (Managers only)
3. POST,PUT,PATCH,DELETE /api/menu-items/ - Denies access and return 403 Unauthorized (Customer, Delivery Crew)
4. GET /api/menu-items/{menuItem} - List single menu item (Customer, Delivery Crew, Manager)
5. POST,PUT,PATCH,DELETE /api/menu-items/{menuItem} - Denies access and return 403 Unauthorized (Customer, Delivery Crew)
6. GET /api/menu-items - Lists all menu items (Manager)	
7. POST /api/menu-items - Creates a new menu item and returns 201 - Created	(Manager)	
8. PUT, PATCH /api/menu-items/{menuItem} - Updates single menu item	(Manager)		
9. DELETE /api/menu-items/{menuItem} - Deletes menu item (Manager)		
   
C. User group management endpoints
1. GET /api/groups/manager/users - Returns all managers	(Admin)
2. POST /api/groups/manager/users - Assigns the user in the payload to the manager group and returns 201-Created (Admin)
3. DELETE /api/groups/manager/users/{userId} - Removes this particular user from the manager group and returns 200-Success if everything is okay, 404-Not found if the user is not found (Admin)
4. GET /api/groups/delivery-crew/users - Returns all delivery crew (Manager)
5. POST /api/groups/delivery-crew/users - Assigns the user in the payload to delivery crew group and returns 201-Created (Manager)
6. DELETE /api/groups/delivery-crew/users/{userId} - Removes this user from the delivery crew group and returns 200-Success if everything is okay, 404-Not found if the user is not found (Manager)


D. Cart management endpoints
1. GET /api/cart/menu-items - Returns current items in the cart for the current user (Customer)
2. POST /api/cart/menu-items - Adds the menu item to the cart. Sets the authenticated user as the user id for these cart items (Customer)
3. DELETE /api/cart/menu-items - Deletes all menu items created by the current user (Customer)
   
E. Order management endpoints
1. GET /api/orders - Returns all orders with order items created by this user (Customer)
2. POST /api/orders - Creates a new order item for the current user. Gets current cart items from the cart endpoints and adds those items to the order items table. Then deletes all items from the cart for this user (Customer)
3. GET /api/orders/{orderId} - Returns all items for this order ID. If the order ID doesn’t belong to the current user, it displays an appropriate HTTP error status code (Customer)
4. GET /api/orders - Returns all orders with order items by all users (Manager)
5. PUT, PATCH /api/orders/{orderId} - Updates the order. A manager can use this endpoint to set a delivery crew to this order, and also update the order status to 0 or 1. If a delivery crew is assigned to this order and the status = 0, it means the order is out for delivery. If a delivery crew is assigned to this order and the status = 1, it means the order has been delivered (Manager)
6. DELETE /api/orders/{orderId} - Deletes this order (Manager)
7. GET /api/orders - Returns all orders with order items assigned to the delivery crew (Delivery crew)
8. PATCH /api/orders/{orderId} - A delivery crew can use this endpoint to update the order status to 0 or 1. The delivery crew will not be able to update anything else in this order (Delivery crew)

**Additional Functionalities**

1. Filtering, Pagination, and Sorting for /api/menu-items and /api/orders
2. Throttling - Throttling has been applied to both authenticated and unauthenticated users to limit the number of requests they can make to the API within a specified time frame.
