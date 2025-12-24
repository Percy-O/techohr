from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'is_student']
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'bio', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'bio': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'rows': 4}),
        }

class AdminCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary bg-transparent text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500'}),
            'password1': forms.PasswordInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary bg-transparent text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500'}),
            'password2': forms.PasswordInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary bg-transparent text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500'}),
        }
