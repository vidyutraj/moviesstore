from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')

    def __str__(self):
        return str(self.id) + ' - ' + self.name
    
    def get_average_rating(self):
        """Calculate the average rating for this movie"""
        from django.db.models import Avg
        avg_rating = self.rating_set.aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 1) if avg_rating else 0
    
    def get_rating_count(self):
        """Get the total number of ratings for this movie"""
        return self.rating_set.count()
    
    def get_user_rating(self, user):
        """Get the rating given by a specific user for this movie"""
        if user.is_authenticated:
            try:
                return self.rating_set.get(user=user).rating
            except Rating.DoesNotExist:
                return None
        return None
    
    def get_star_display(self):
        """Get a list of star states for display (filled, half, empty)"""
        avg_rating = self.get_average_rating()
        stars = []
        
        for i in range(1, 6):
            if i <= int(avg_rating):
                stars.append('filled')
            elif i == int(avg_rating) + 1 and avg_rating % 1 >= 0.5:
                stars.append('half')
            else:
                stars.append('empty')
        
        return stars

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name

class Petition(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    votes = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')

    def __str__(self):
        return self.title

    def get_vote_count(self):
        return self.vote_set.count()


class Vote(models.Model):
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('petition', 'user')  # Ensures one vote per user

    def __str__(self):
        return f"{self.user.username} voted on {self.petition.title}"


class Rating(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('movie', 'user')  # Ensures one rating per user per movie

    def __str__(self):
        return f"{self.user.username} rated {self.movie.name} {self.rating} stars"