from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cart.models import Cart

class Command(BaseCommand):
    help = 'Create sample carts for testing'

    def handle(self, *args, **options):
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
            self.stdout.write(
                self.style.SUCCESS(f'Created test user: {user.username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Test user already exists: {user.username}')
            )

        # Create sample carts
        sample_carts = ['My Favorites', 'Action Movies', 'Comedy Collection']
        
        for cart_name in sample_carts:
            cart, created = Cart.objects.get_or_create(
                user=user,
                name=cart_name
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created cart: {cart_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Cart already exists: {cart_name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Sample carts setup completed!')
        )
