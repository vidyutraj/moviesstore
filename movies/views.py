from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Like
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    
    # Add like status for each review if user is authenticated
    if request.user.is_authenticated:
        for review in reviews:
            review.user_liked = review.is_liked_by_user(request.user)
    else:
        for review in reviews:
            review.user_liked = False

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

def top_comments(request):
    # Get all reviews ordered by like count (most liked first) and limit to top 10
    from django.db.models import Count
    top_reviews = Review.objects.select_related('user', 'movie').annotate(
        like_count=Count('like')
    ).order_by('-like_count', '-date')[:10]
    
    # Add like status for each review if user is authenticated
    if request.user.is_authenticated:
        for review in top_reviews:
            review.user_liked = review.is_liked_by_user(request.user)
    else:
        for review in top_reviews:
            review.user_liked = False
    
    template_data = {}
    template_data['title'] = 'Top Comments'
    template_data['top_reviews'] = top_reviews
    return render(request, 'movies/top_comments.html', {'template_data': template_data})

@login_required
def toggle_like(request, review_id):
    if request.method == 'POST':
        review = get_object_or_404(Review, id=review_id)
        like, created = Like.objects.get_or_create(review=review, user=request.user)
        
        if not created:
            # Like already exists, so remove it (unlike)
            like.delete()
            liked = False
        else:
            # Like was created
            liked = True
        
        like_count = review.get_like_count()
        
        return JsonResponse({
            'liked': liked,
            'like_count': like_count
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)