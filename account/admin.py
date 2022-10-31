from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CUser
from .forms import CustomUserChangeForm, CustomUserCreationForm


# Register your models here.

@admin.register(CUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = None
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
