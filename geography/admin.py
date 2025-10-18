from django.contrib import admin
from .models import Region, UserLocation, MoviePopularity

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'state', 'city', 'population']
    list_filter = ['country', 'state']
    search_fields = ['name', 'city', 'state']
    ordering = ['name']

@admin.register(UserLocation)
class UserLocationAdmin(admin.ModelAdmin):
    list_display = ['user', 'region', 'latitude', 'longitude', 'updated_at']
    list_filter = ['region__country', 'region__state']
    search_fields = ['user__username', 'region__name']
    ordering = ['user__username']

@admin.register(MoviePopularity)
class MoviePopularityAdmin(admin.ModelAdmin):
    list_display = ['movie', 'region', 'purchase_count', 'view_count', 'last_updated']
    list_filter = ['region__country', 'region__state', 'last_updated']
    search_fields = ['movie__name', 'region__name']
    ordering = ['-purchase_count']