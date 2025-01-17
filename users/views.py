from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView


from .form import UserRegestrationForm, UserLoginForm, ProfileEditForm, PostCreateForm
from .models import User, Profile, Statistics, Posts

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
            Statistics.objects.create(user=self.object)

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
    context = {
        'user': User.objects.get(username=username)
    }
    return render(request, 'users/profile.html', context=context)


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