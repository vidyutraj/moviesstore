from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Movie, Review, Petition, Vote
from django.contrib.auth.decorators import login_required

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
        return redirect('movies:show', id=id)
    else:
        return redirect('movies:show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies:show', id=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies:show', id=id)
    else:
        return redirect('movies:show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies:show', id=id)

# View to list all petitions
def petition_list(request):
    petitions = Petition.objects.all().order_by('-created_at')
    template_data = {
        'title': 'Movie Petitions',
        'petitions': petitions,
    }
    return render(request, 'movies/petition_list.html', {'template_data': template_data})

# View to create a new petition
@login_required
def create_petition(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        if title and description:
            petition = Petition.objects.create(
                title=title,
                description=description,
                requested_by=request.user
            )
            messages.success(request, 'Petition created successfully!')
            return redirect('movies:petition_detail', petition_id=petition.id)
        else:
            messages.error(request, 'Please fill in all fields.')
    
    template_data = {'title': 'Create Movie Petition'}
    return render(request, 'movies/create_petition.html', {'template_data': template_data})

# View to see details of a petition
def petition_detail(request, petition_id):
    petition = get_object_or_404(Petition, id=petition_id)
    has_voted = False
    if request.user.is_authenticated:
        has_voted = Vote.objects.filter(petition=petition, user=request.user).exists()
    
    template_data = {
        'title': petition.title,
        'petition': petition,
        'has_voted': has_voted,
        'vote_count': petition.get_vote_count(),
    }
    return render(request, 'movies/petition_detail.html', {'template_data': template_data})

# View to record a user's vote
@login_required
def vote_petition(request, petition_id):
    petition = get_object_or_404(Petition, id=petition_id)
    
    # Check if user already voted
    if Vote.objects.filter(petition=petition, user=request.user).exists():
        messages.error(request, 'You have already voted on this petition.')
    else:
        Vote.objects.create(petition=petition, user=request.user)
        messages.success(request, 'Your vote has been recorded!')
    
    return redirect('movies:petition_detail', petition_id=petition.id)