from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from users.models import Posts, User, Followers

# Create your views here.
@login_required(login_url='/login/')
def main(request):
    posts = Posts.objects.all()
    for post in posts:
        post.is_liked = post.likes.filter(pk=request.user.pk).exists()

    followed_users = Followers.objects.filter(follower=request.user).values_list('following', flat=True)
    not_followed_users = User.objects.exclude(pk=request.user.pk).exclude(pk__in=followed_users)
    context ={
        'posts': posts,
        'users': not_followed_users
    }
    return render(request, 'main/main.html', context=context)