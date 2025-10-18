from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie

class Region(models.Model):
    """Represents a geographic region for movie popularity tracking"""
    name = models.CharField(max_length=100)
    latitude = models.FloatField()  # Center latitude for the region
    longitude = models.FloatField()  # Center longitude for the region
    population = models.IntegerField(default=0)  # Region population for context
    country = models.CharField(max_length=50, default='USA')
    state = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class UserLocation(models.Model):
    """Tracks user location for purchase attribution"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.region.name if self.region else 'Unknown Location'}"

class MoviePopularity(models.Model):
    """Tracks movie popularity metrics by region"""
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    purchase_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)  # For future use if views are tracked
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('movie', 'region')
        ordering = ['-purchase_count']
    
    def __str__(self):
        return f"{self.movie.name} in {self.region.name} - {self.purchase_count} purchases"
    
    def get_trending_score(self):
        """Calculate a trending score based on purchases and recency"""
        # Simple trending calculation - can be enhanced
        return self.purchase_count