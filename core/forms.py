from django import forms
from .models import Project, Testimonial, SiteSettings, Employee, CompanyStats

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'image', 'client', 'url', 'technologies', 'featured']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'rows': 5}),
            'client': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'technologies': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'placeholder': 'Comma-separated tags (e.g. React, Django)'}),
            'featured': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-primary border-gray-300 dark:border-gray-600 rounded focus:ring-primary bg-gray-100 dark:bg-gray-700'}),
        }

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['client_name', 'position', 'company', 'content', 'image', 'rating']
        widgets = {
            'client_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'position': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'company': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'content': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'rows': 4}),
            'rating': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'min': 1, 'max': 5}),
        }

class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            'site_name', 'logo', 'favicon', 'logo_light', 'logo_dark',
            'address', 'email_primary', 'email_support', 'phone_primary',
            'facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url',
            'map_embed_url'
        ]
        widgets = {
            'site_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
            'address': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
            'email_primary': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
            'email_support': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
            'phone_primary': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
            'facebook_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
            'twitter_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
            'instagram_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
            'map_embed_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40', 'placeholder': 'https://www.google.com/maps/embed?...'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['logo'].widget = forms.FileInput(attrs={'class': 'hidden', 'accept': 'image/*'})
        self.fields['favicon'].widget = forms.FileInput(attrs={'class': 'hidden', 'accept': 'image/*'})
        self.fields['logo_light'].widget = forms.FileInput(attrs={'class': 'hidden', 'accept': 'image/*'})
        self.fields['logo_dark'].widget = forms.FileInput(attrs={'class': 'hidden', 'accept': 'image/*'})

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'role', 'photo', 'linkedin_url', 'twitter_url', 'github_url', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
            'role': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
            'twitter_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
            'github_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
            'order': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['photo'].widget = forms.FileInput(attrs={'class': 'hidden', 'accept': 'image/*'})

class CompanyStatsForm(forms.ModelForm):
    class Meta:
        model = CompanyStats
        fields = ['projects_completed', 'happy_clients', 'team_members', 'experience_years']
        widgets = {
            'projects_completed': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
            'happy_clients': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
            'team_members': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
            'experience_years': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40'}),
        }
