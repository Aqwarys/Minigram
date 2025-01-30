from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile, Posts, Community

class UserRegestrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture', 'phone_number', 'date_of_birth', 'gender']


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Posts
        fields = ['image', 'description']


class CreateCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['avatar', 'banner', 'name', 'description', 'link']