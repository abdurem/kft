from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Product

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'role')

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price']