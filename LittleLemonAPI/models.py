from django.db import models
from django.contrib.auth.models import User

# Category model to classify menu items
class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.title

# MenuItem model to store the menu items
class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.title

# Cart model to track items added to the user's cart
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, editable=False) # Price per item
    price = models.DecimalField(max_digits=6, decimal_places=2, editable=False)  # Prevent manual edits, Total price for this item in cart

    class Meta:
        unique_together = ('menuitem', 'user')

    def save(self, *args, **kwargs):
        """Ensure unit_price is always taken from menuitem and update price"""
        self.unit_price = self.menuitem.price  # Always set unit_price to menuitem.price
        self.price = self.unit_price * self.quantity  # Calculate total price
        super().save(*args, **kwargs)  # Call original save method
        
    def __str__(self):
        return f"{self.quantity}x {self.menuitem.title} @{self.unit_price} each for {self.user.username} - Total: ${self.price}"

# Order model to track customer orders
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='delivery_crew', null=True)
    status = models.BooleanField(db_index=True, default=0)  # 0 = out for delivery, 1 = delivered
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Store total in DB
    date = models.DateTimeField(auto_now_add=True)  # Store both date and time

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

# OrderItems model to track the items in each order
class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('order', 'menuitem')

    def __str__(self):
        return f"{self.quantity} x {self.menuitem.title} in Order #{self.order.id}"
