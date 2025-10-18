from django.core.management.base import BaseCommand
from geography.models import Region, MoviePopularity
from movies.models import Movie
from django.contrib.auth.models import User
import random

class Command(BaseCommand):
    help = 'Populate sample geographic data for testing the popularity map'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample regions...')
        
        # Create sample regions
        regions_data = [
            {
                'name': 'Atlanta Metro',
                'latitude': 33.7490,
                'longitude': -84.3880,
                'country': 'USA',
                'state': 'Georgia',
                'city': 'Atlanta',
                'population': 498715
            },
            {
                'name': 'New York City',
                'latitude': 40.7128,
                'longitude': -74.0060,
                'country': 'USA',
                'state': 'New York',
                'city': 'New York',
                'population': 8336817
            },
            {
                'name': 'Los Angeles',
                'latitude': 34.0522,
                'longitude': -118.2437,
                'country': 'USA',
                'state': 'California',
                'city': 'Los Angeles',
                'population': 3971883
            },
            {
                'name': 'Chicago',
                'latitude': 41.8781,
                'longitude': -87.6298,
                'country': 'USA',
                'state': 'Illinois',
                'city': 'Chicago',
                'population': 2693976
            },
            {
                'name': 'Miami',
                'latitude': 25.7617,
                'longitude': -80.1918,
                'country': 'USA',
                'state': 'Florida',
                'city': 'Miami',
                'population': 467963
            },
            {
                'name': 'Seattle',
                'latitude': 47.6062,
                'longitude': -122.3321,
                'country': 'USA',
                'state': 'Washington',
                'city': 'Seattle',
                'population': 749256
            }
        ]
        
        created_regions = []
        for region_data in regions_data:
            region, created = Region.objects.get_or_create(
                name=region_data['name'],
                defaults=region_data
            )
            created_regions.append(region)
            if created:
                self.stdout.write(f'Created region: {region.name}')
            else:
                self.stdout.write(f'Region already exists: {region.name}')
        
        # Get all movies
        movies = Movie.objects.all()
        if not movies.exists():
            self.stdout.write('No movies found. Please add some movies first.')
            return
        
        self.stdout.write('Creating sample movie popularity data...')
        
        # Create sample popularity data
        for region in created_regions:
            # Randomly select 3-5 movies for each region
            num_movies = random.randint(3, 5)
            selected_movies = random.sample(list(movies), min(num_movies, len(movies)))
            
            for movie in selected_movies:
                # Generate random purchase counts
                purchase_count = random.randint(1, 150)
                
                movie_popularity, created = MoviePopularity.objects.get_or_create(
                    movie=movie,
                    region=region,
                    defaults={'purchase_count': purchase_count}
                )
                
                if created:
                    self.stdout.write(f'Created popularity data: {movie.name} in {region.name} - {purchase_count} purchases')
                else:
                    # Update existing data with new random count
                    movie_popularity.purchase_count = purchase_count
                    movie_popularity.save()
                    self.stdout.write(f'Updated popularity data: {movie.name} in {region.name} - {purchase_count} purchases')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated sample data with {len(created_regions)} regions and popularity data for {len(movies)} movies'
            )
        )
