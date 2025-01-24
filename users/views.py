from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.db.models import Count


from .form import UserRegestrationForm, UserLoginForm, ProfileEditForm, PostCreateForm
from .models import User, Profile, Posts, Likes, Followers, Bookmark

# Create your views here.
class UserRegestration(CreateView):
    form_class = UserRegestrationForm
    template_name = 'users/regestration.html'
    success_url = reverse_lazy('main:main')

    def form_valid(self, form):
        # Сохраняем объект пользователя
        response = super().form_valid(form)

        # Убедимся, что объект пользователя создан
        if self.object:
            # Создаем связанные объекты Profile и Statistics
            Profile.objects.create(user=self.object)

            # Аутентифицируем пользователя
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(self.request, email=email, password=password)

            if user is not None:
                login(self.request, user=user)

        return response

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('main:main')


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileEditForm
    template_name = 'users/edit_profile.html'
    success_url = reverse_lazy('users:user_profile')
    login_url = '/login/'

    def get_object(self, queryset = None):
        return self.request.user.profile


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.get(email=email)
            if user is not None and user.check_password(password):
                login(request, user)
                return redirect(reverse_lazy('main:main'))
    context = {
        'form': UserLoginForm
    }
    return render(request, 'users/login.html', context=context)


@login_required(login_url='/login/')
def profile(request, username):
    profile_user = User.objects.get(username=username)
    is_following = Followers.objects.filter(follower=request.user, following=profile_user).exists()
    context = {
        'user': profile_user,
        'is_following': is_following
    }
    return render(request, 'users/profile.html', context=context)
# User.objects.annotate(
#         posts_count=Count('posts'),
#         follower_count=Count('followers'),
#         following_count=Count('following'),
#     ).get(username=username),

@login_required(login_url='/login/')
def user_profile(request):
        return render(request, 'users/profile.html')

@login_required(login_url='/login/')
def create_post(request):
    if request.method == 'POST':
        form = PostCreateForm(request.POST, request.FILES)
        if form.is_valid():
            Posts.objects.create(user=request.user,
                                 image=form.cleaned_data['image'],
                                 description=form.cleaned_data['description']
                                )
            return redirect('users:user_profile')
    else:
        form = PostCreateForm

    context = {
        'form': form
    }
    return render(request, 'users/create_post.html', context=context)

@login_required(login_url='/login/')
def view_post(request, post_id):
    post = Posts.objects.prefetch_related('likes').get(pk=post_id)
    is_liked = post.likes.filter(pk=request.user.pk).exists()
    is_bookmarked = post.bookmarks.filter(pk=request.user.pk).exists()

    context = {
        'post': post,
        'is_liked': is_liked,
        'is_bookmarked': is_bookmarked
    }
    return render(request, 'users/post.html', context=context)

@login_required(login_url='/login/')
def like(request, post_id):
    post = get_object_or_404(Posts, pk=post_id)
    like, created = Likes.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()

    previous_url = request.META.get('HTTP_REFERER', 'users:feed')  # Указываем fallback на feed, если HTTP_REFERER пустой
    return redirect(previous_url)
    # return redirect('users:post_view', post_id=post_id)


@login_required(login_url='/login/')
def follow(request, user_pk):
    user1 = request.user  # Текущий пользователь
    user2 = get_object_or_404(User, pk=user_pk)  # Пользователь, на которого подписываются

    if user1 == user2:
        # Запрещаем подписываться на самого себя
        return redirect('users:profile', username=user2.username)

    # Получаем или создаём связь
    follow, created = Followers.objects.get_or_create(follower=user1, following=user2)

    if not created:
        # Если связь уже существует, удаляем её
        follow.delete()

    return redirect('users:profile', username=user2.username)


@login_required(login_url='/login/')
def followers(request, username):
    user = get_object_or_404(User, username=username)
    followers = Followers.objects.filter(following=user)
    context = {
        'followers': followers,
        'user': user
    }
    return render(request, 'users/followers.html', context=context)


@login_required(login_url='/login/')
def following(request, username):
    user = get_object_or_404(User, username=username)
    following = Followers.objects.filter(follower=user)
    context = {
        'following': following,
        'user': user
    }
    return render(request, 'users/following.html', context=context)




@login_required(login_url='/login/')
def friends(request, username):
    user1 = get_object_or_404(User, username=username)

    friends = User.objects.filter(
        followers__follower=user1,
        following__following=user1
    ).distinct()

    context = {
        'user': user1,
        'friends': friends
    }
    return render(request, 'users/friends.html', context=context)


@login_required(login_url='/login/')
def bookmark(request, post_id):
    post = get_object_or_404(Posts, pk=post_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)

    if not created:
        bookmark.delete()

    previous_url = request.META.get('HTTP_REFERER', 'users:feed')  # Указываем fallback на feed, если HTTP_REFERER пустой
    return redirect(previous_url)


@login_required(login_url='/login/')
def bookmarks_view(request):
    user = request.user
    context = {
        'bookmarks': Bookmark.objects.filter(user=user)
    }
    return render(request, 'users/bookmarks.html', context=context)