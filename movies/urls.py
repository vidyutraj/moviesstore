from django.urls import path
from . import views

app_name = 'movies'  # make sure this is included

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:id>/', views.show, name='show'),
    path('<int:id>/review/create/', views.create_review, name='create_review'),
    path('<int:id>/review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('<int:id>/review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    # Petition URLs
    path('petitions/', views.petition_list, name='petition_list'),
    path('petitions/create/', views.create_petition, name='create_petition'),
    path('petitions/<int:petition_id>/', views.petition_detail, name='petition_detail'),
    path('petitions/<int:petition_id>/vote/', views.vote_petition, name='vote_petition'),
]