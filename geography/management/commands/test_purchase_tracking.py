from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from geography.models import Region, UserLocation, MoviePopularity
from movies.models import Movie
from cart.models import Cart, CartItem, Order, Item
import random

class Command(BaseCommand):
    help = 'Test purchase tracking functionality by creating sample orders'

    def handle(self, *args, **options):
        self.stdout.write('Testing purchase tracking functionality...')
        
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write('Created test user: testuser')
        else:
            self.stdout.write('Using existing test user: testuser')
        
        # Get a region and set user location
        regions = Region.objects.all()
        if not regions.exists():
            self.stdout.write('No regions found. Please run populate_sample_data first.')
            return
        
        test_region = regions.first()
        user_location, created = UserLocation.objects.get_or_create(
            user=user,
            defaults={
                'region': test_region,
                'latitude': test_region.latitude,
                'longitude': test_region.longitude
            }
        )
        
        if created:
            self.stdout.write(f'Set user location to: {test_region.name}')
        else:
            self.stdout.write(f'User already has location: {user_location.region.name}')
        
        # Get some movies
        movies = Movie.objects.all()
        if not movies.exists():
            self.stdout.write('No movies found. Please add some movies first.')
            return
        
        # Show current popularity before purchase
        self.stdout.write('\n--- BEFORE PURCHASE ---')
        for movie in movies[:3]:  # Show first 3 movies
            try:
                popularity = MoviePopularity.objects.get(movie=movie, region=test_region)
                self.stdout.write(f'{movie.name} in {test_region.name}: {popularity.purchase_count} purchases')
            except MoviePopularity.DoesNotExist:
                self.stdout.write(f'{movie.name} in {test_region.name}: 0 purchases')
        
        # Create a test cart and order
        cart, created = Cart.objects.get_or_create(
            user=user,
            name='Test Cart',
            defaults={}
        )
        
        # Add a movie to cart
        test_movie = movies.first()
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            movie=test_movie,
            defaults={
                'quantity': 2,  # Purchase 2 copies
                'price': test_movie.price
            }
        )
        
        if created:
            self.stdout.write(f'Added {test_movie.name} to cart (quantity: 2)')
        else:
            cart_item.quantity = 2
            cart_item.save()
            self.stdout.write(f'Updated cart item: {test_movie.name} (quantity: 2)')
        
        # Create an order (this should trigger the signal)
        order = Order.objects.create(
            user=user,
            total=cart.get_total(),
            cart=cart
        )
        
        # Create order items
        for cart_item in cart.cartitem_set.all():
            Item.objects.create(
                order=order,
                movie=cart_item.movie,
                quantity=cart_item.quantity,
                price=cart_item.price
            )
        
        self.stdout.write(f'Created order {order.id} for user {user.username}')
        
        # Show popularity after purchase
        self.stdout.write('\n--- AFTER PURCHASE ---')
        for movie in movies[:3]:
            try:
                popularity = MoviePopularity.objects.get(movie=movie, region=test_region)
                self.stdout.write(f'{movie.name} in {test_region.name}: {popularity.purchase_count} purchases')
            except MoviePopularity.DoesNotExist:
                self.stdout.write(f'{movie.name} in {test_region.name}: 0 purchases')
        
        # Test with another movie in a different region
        if regions.count() > 1:
            other_region = regions[1]
            other_movie = movies[1] if movies.count() > 1 else movies.first()
            
            # Create another user in different region
            other_user, created = User.objects.get_or_create(
                username='testuser2',
                defaults={
                    'email': 'test2@example.com',
                    'first_name': 'Test',
                    'last_name': 'User2'
                }
            )
            if created:
                other_user.set_password('testpass123')
                other_user.save()
            
            UserLocation.objects.get_or_create(
                user=other_user,
                defaults={
                    'region': other_region,
                    'latitude': other_region.latitude,
                    'longitude': other_region.longitude
                }
            )
            
            # Create order for second user
            other_cart, created = Cart.objects.get_or_create(
                user=other_user,
                name='Test Cart 2'
            )
            
            CartItem.objects.get_or_create(
                cart=other_cart,
                movie=other_movie,
                defaults={
                    'quantity': 1,
                    'price': other_movie.price
                }
            )
            
            other_order = Order.objects.create(
                user=other_user,
                total=other_cart.get_total(),
                cart=other_cart
            )
            
            for cart_item in other_cart.cartitem_set.all():
                Item.objects.create(
                    order=other_order,
                    movie=cart_item.movie,
                    quantity=cart_item.quantity,
                    price=cart_item.price
                )
            
            self.stdout.write(f'Created order for {other_user.username} in {other_region.name}')
            
            # Show popularity in both regions
            self.stdout.write('\n--- REGIONAL COMPARISON ---')
            for region in [test_region, other_region]:
                self.stdout.write(f'\n{region.name}:')
                for movie in [test_movie, other_movie]:
                    try:
                        popularity = MoviePopularity.objects.get(movie=movie, region=region)
                        self.stdout.write(f'  {movie.name}: {popularity.purchase_count} purchases')
                    except MoviePopularity.DoesNotExist:
                        self.stdout.write(f'  {movie.name}: 0 purchases')
        
        self.stdout.write(
            self.style.SUCCESS('\nPurchase tracking test completed successfully!')
        )
