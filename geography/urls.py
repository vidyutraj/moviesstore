from django.urls import path
from . import views

urlpatterns = [
    path('', views.popularity_map, name='geography.popularity_map'),
    path('settings/', views.user_location_settings, name='geography.location_settings'),
    path('region/<int:region_id>/', views.region_detail, name='geography.region_detail'),
    path('api/region/<int:region_id>/trending/', views.api_region_trending, name='geography.api_region_trending'),
    path('api/set-location/', views.api_set_location, name='geography.api_set_location'),
]
