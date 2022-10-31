from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CUser
        fields = ['username', 'email', 'first_name', 'last_name']


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CUser
        fields = '__all__'
