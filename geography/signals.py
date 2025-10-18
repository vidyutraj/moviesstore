from django.db.models.signals import post_save
from django.dispatch import receiver
from cart.models import Order, Item
from geography.models import MoviePopularity, UserLocation

@receiver(post_save, sender=Item)
def update_movie_popularity_on_item(sender, instance, created, **kwargs):
    """Update movie popularity when a new item is added to an order"""
    if created:
        # Get the user's location
        try:
            user_location = UserLocation.objects.get(user=instance.order.user)
            
            if user_location.region:
                movie_popularity, created = MoviePopularity.objects.get_or_create(
                    movie=instance.movie,
                    region=user_location.region,
                    defaults={'purchase_count': 0}
                )
                
                movie_popularity.purchase_count += instance.quantity
                movie_popularity.save()
                
        except UserLocation.DoesNotExist:
            # User location not set, skip updating popularity
            pass
