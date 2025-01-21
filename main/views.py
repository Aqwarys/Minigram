from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from users.models import Posts

# Create your views here.
@login_required(login_url='/login/')
def main(request):
    posts = Posts.objects.all()
    for post in posts:
        post.is_liked = post.likes.filter(pk=request.user.pk).exists()
    context ={
        'posts': posts
    }
    return render(request, 'main/main.html', context=context)