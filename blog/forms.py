from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    tags_input = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'placeholder': 'Separate tags with commas'}), help_text="Separate tags with commas.")

    class Meta:
        model = Post
        fields = ['title', 'category', 'content', 'image', 'is_featured', 'meta_title', 'meta_description', 'visibility']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'content': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'rows': 10}),
            'meta_title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'meta_description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'rows': 3}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-primary border-gray-300 dark:border-gray-600 rounded focus:ring-primary bg-gray-100 dark:bg-gray-700'}),
            'visibility': forms.Select(attrs={'class': 'w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-xs focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['tags_input'].initial = ", ".join([t.name for t in self.instance.tags.all()])

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'placeholder': 'Your Email'}),
            'body': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'rows': 4, 'placeholder': 'Your Comment'}),
        }
