from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie

class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'name')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    def get_total(self):
        total = 0
        for item in self.cartitem_set.all():
            total += item.price * item.quantity
        return total

    def get_item_count(self):
        return sum(item.quantity for item in self.cartitem_set.all())

class CartItem(models.Model):
    id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()  # Store price at time of adding to cart

    class Meta:
        unique_together = ('cart', 'movie')

    def __str__(self):
        return f"{self.cart.name} - {self.movie.name} x{self.quantity}"

    def get_subtotal(self):
        return self.price * self.quantity

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    total = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.id) + ' - ' + self.user.username

class Item(models.Model):
    id = models.AutoField(primary_key=True)
    price = models.IntegerField()
    quantity = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name