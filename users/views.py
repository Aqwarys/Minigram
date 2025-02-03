from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.db.models import Count


from .form import UserRegestrationForm, UserLoginForm, ProfileEditForm, PostCreateForm, CreateCommunityForm, CreateCommentForm
from .models import (User,
                     Profile,
                     Posts,
                     Likes,
                     Followers,
                     Bookmark,
                     Community,
                     Community_Follow,
                     Comments
                     )


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
    posts = Posts.objects.filter(user=profile_user, community=None).select_related('user')
    context = {
        'user': profile_user,
        'is_following': is_following,
        'posts': posts
    }
    return render(request, 'users/profile.html', context=context)
# User.objects.annotate(
#         posts_count=Count('posts'),
#         follower_count=Count('followers'),
#         following_count=Count('following'),
#     ).get(username=username),

@login_required(login_url='/login/')
def user_profile(request):
    posts = Posts.objects.filter(user=request.user, community=None).select_related('user')
    context = {
        'posts': posts
    }
    return render(request, 'users/profile.html', context=context)

@login_required(login_url='/login/')
def create_post(request):
    if request.method == 'POST':
        form = PostCreateForm(request.POST, request.FILES)
        community_id = request.POST.get('community_id')  # Получаем ID сообщества из POST-запроса

        if form.is_valid():
            community = None

            # Если передан community_id, находим сообщество
            if community_id:
                community = get_object_or_404(Community, id=community_id)

                # Проверяем, что пользователь — владелец сообщества
                if community.owner != request.user:
                    return render(request, 'users/create_post.html', {
                        'form': form,
                        'error': 'You are not the owner of this community.'
                    })

            # Создаём пост
            Posts.objects.create(
                user=request.user,
                community=community,
                image=form.cleaned_data['image'],
                description=form.cleaned_data['description']
            )
            return redirect('users:user_profile')  # Перенаправление на профиль пользователя
    else:
        form = PostCreateForm()

    context = {
        'form': form,
        'communities': Community.objects.filter(owner=request.user)  # Доступные сообщества
    }
    return render(request, 'users/create_post.html', context=context)

@login_required(login_url='/login/')
def view_post(request, post_id):
    post = Posts.objects.prefetch_related('likes').get(pk=post_id)
    is_liked = post.likes.filter(pk=request.user.pk).exists()
    is_bookmarked = post.bookmarks.filter(pk=request.user.pk).exists()
    comments = Comments.objects.filter(post=post)

    context = {
        'post': post,
        'is_liked': is_liked,
        'is_bookmarked': is_bookmarked,
        'comments': comments,
        'form': CreateCommentForm()
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

    previous_url = request.META.get('HTTP_REFERER', 'users:feed')  # Указываем fallback на feed, если HTTP_REFERER пустой
    return redirect(previous_url)

@login_required(login_url='/login/')
def follower_remove(request, user_pk):
    user1 = request.user
    user2 = get_object_or_404(User, pk=user_pk)

    followed = Followers.objects.filter(follower=user2, following=user1)
    if followed.exists():
        followed.delete()

    previous_url = request.META.get('HTTP_REFERER', 'users:feed')  # Указываем fallback на feed, если HTTP_REFERER пустой
    return redirect(previous_url)

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

@login_required(login_url='/login/')
def community_view(request, slugger):
    community = Community.objects.get(slug=slugger)
    is_following = Community_Follow.objects.filter(user=request.user, community=community).exists()
    posts = Posts.objects.filter(community=community).select_related('user')
    context = {
        'community': community,
        'is_following': is_following,
        'posts': posts
    }

    return render(request, 'users/community.html', context=context)

@login_required(login_url='/login/')
def community_follow(request, slugger):
    user = request.user
    community = get_object_or_404(Community, slug=slugger)

    if user == community.owner:
        return redirect('users:community', slugger=slugger)

    follow, created = Community_Follow.objects.get_or_create(user=user, community=community)

    if not created:
        follow.delete()

    previous_url = request.META.get('HTTP_REFERER', 'users:feed')  # Указываем fallback на feed, если HTTP_REFERER пустой
    return redirect(previous_url)


@login_required(login_url='/login/')
def community_list(request):
    user = request.user
    communities = Community.objects.exclude(
        id__in=Community_Follow.objects.filter(user=user).values_list("community_id", flat=True)
    ).exclude(owner=user)

    user_communites = Community_Follow.objects.filter(user=user)
    own_community = Community.objects.filter(owner=user)
    context = {
        'communities': communities,
        'user_communities': user_communites,
        'own_community': own_community
    }

    return render(request, 'users/communities.html', context=context)


@login_required(login_url='/login/')
def create_community(request):
    if request.method == 'POST':
        form = CreateCommunityForm(request.POST, request.FILES)
        if form.is_valid():
            community = form.save(commit=False)
            community.owner = request.user
            community.save()
            return redirect('users:community', slugger=community.slug)
    else:
        form = CreateCommunityForm()
    context = {
        'form': form
    }
    return render(request, 'users/create_community.html', context=context)


@login_required(login_url='/login/')
def comment_create(request, post_id):
    if request.method == 'POST':
        form = CreateCommentForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            post = get_object_or_404(Posts, pk=post_id)
            Comments.objects.create(post=post, text=text, user=request.user)
            return redirect('users:post_view', post_id=post.pk)

    return redirect('users:post_view', post_id=post_id)