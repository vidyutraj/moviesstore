from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from .models import Region, MoviePopularity, UserLocation
from movies.models import Movie
from cart.models import Order, Item
import json
import math

def popularity_map(request):
    """Display the geographic popularity map"""
    regions = Region.objects.all()
    
    # Get movie popularity data for all regions
    popularity_data = []
    for region in regions:
        region_movies = MoviePopularity.objects.filter(region=region).order_by('-purchase_count')[:5]
        region_data = {
            'id': region.id,
            'name': region.name,
            'latitude': region.latitude,
            'longitude': region.longitude,
            'country': region.country,
            'state': region.state,
            'city': region.city,
            'top_movies': [
                {
                    'id': mp.movie.id,
                    'name': mp.movie.name,
                    'purchase_count': mp.purchase_count,
                    'image_url': mp.movie.image.url if mp.movie.image else None
                }
                for mp in region_movies
            ]
        }
        popularity_data.append(region_data)
    
    context = {
        'regions': regions,
        'popularity_data': json.dumps(popularity_data),
        'title': 'Movie Popularity Map'
    }
    return render(request, 'geography/popularity_map.html', context)

def region_detail(request, region_id):
    """Get detailed trending movies for a specific region"""
    region = get_object_or_404(Region, id=region_id)
    
    # Get top trending movies for this region
    trending_movies = MoviePopularity.objects.filter(region=region).order_by('-purchase_count')[:10]
    
    # Format the data
    movies_data = []
    for mp in trending_movies:
        movie_data = {
            'id': mp.movie.id,
            'name': mp.movie.name,
            'purchase_count': mp.purchase_count,
            'image_url': mp.movie.image.url if mp.movie.image else None,
            'price': mp.movie.price,
            'description': mp.movie.description[:100] + '...' if len(mp.movie.description) > 100 else mp.movie.description
        }
        movies_data.append(movie_data)
    
    return JsonResponse({
        'region': {
            'id': region.id,
            'name': region.name,
            'country': region.country,
            'state': region.state,
            'city': region.city,
            'population': region.population
        },
        'trending_movies': movies_data
    })

def update_movie_popularity():
    """Utility function to update movie popularity based on recent orders"""
    # This function should be called when orders are completed
    # For now, we'll create a simple implementation
    
    # Get all regions
    regions = Region.objects.all()
    
    for region in regions:
        # Get users in this region
        users_in_region = UserLocation.objects.filter(region=region).values_list('user', flat=True)
        
        # Get recent orders from users in this region
        recent_orders = Order.objects.filter(user__in=users_in_region)
        
        # Count movie purchases by region
        for order in recent_orders:
            items = Item.objects.filter(order=order)
            for item in items:
                movie_popularity, created = MoviePopularity.objects.get_or_create(
                    movie=item.movie,
                    region=region,
                    defaults={'purchase_count': 0}
                )
                movie_popularity.purchase_count += item.quantity
                movie_popularity.save()

def api_region_trending(request, region_id):
    """API endpoint to get trending movies for a region"""
    try:
        region = Region.objects.get(id=region_id)
        trending_movies = MoviePopularity.objects.filter(region=region).order_by('-purchase_count')[:5]
        
        data = {
            'region': region.name,
            'trending_movies': [
                {
                    'movie_id': mp.movie.id,
                    'movie_name': mp.movie.name,
                    'purchase_count': mp.purchase_count,
                    'trending_score': mp.get_trending_score()
                }
                for mp in trending_movies
            ]
        }
        
        return JsonResponse(data)
    except Region.DoesNotExist:
        return JsonResponse({'error': 'Region not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def api_set_location(request):
    """API endpoint to set user location based on coordinates"""
    try:
        data = json.loads(request.body)
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        accuracy = data.get('accuracy', 0)
        
        # Find the nearest region
        nearest_region = find_nearest_region(latitude, longitude)
        
        if not nearest_region:
            return JsonResponse({
                'success': False,
                'message': 'No regions found. Please contact support.'
            })
        
        # Update or create user location
        user_location, created = UserLocation.objects.get_or_create(
            user=request.user,
            defaults={
                'region': nearest_region,
                'latitude': latitude,
                'longitude': longitude
            }
        )
        
        if not created:
            user_location.region = nearest_region
            user_location.latitude = latitude
            user_location.longitude = longitude
            user_location.save()
        
        return JsonResponse({
            'success': True,
            'region_name': nearest_region.name,
            'region_id': nearest_region.id,
            'message': f'Location set to {nearest_region.name}'
        })
        
    except (ValueError, KeyError) as e:
        return JsonResponse({
            'success': False,
            'message': 'Invalid location data provided.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Failed to set location. Please try again.'
        })

def find_nearest_region(latitude, longitude):
    """Find the nearest region to the given coordinates"""
    regions = Region.objects.all()
    
    if not regions.exists():
        return None
    
    nearest_region = None
    min_distance = float('inf')
    
    for region in regions:
        # Calculate distance using Haversine formula
        distance = calculate_distance(
            latitude, longitude,
            region.latitude, region.longitude
        )
        
        if distance < min_distance:
            min_distance = distance
            nearest_region = region
    
    return nearest_region

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

@login_required
def user_location_settings(request):
    """User location settings page"""
    try:
        user_location = UserLocation.objects.get(user=request.user)
    except UserLocation.DoesNotExist:
        user_location = None
    
    context = {
        'user_location': user_location,
        'title': 'Location Settings'
    }
    return render(request, 'geography/location_settings.html', context)