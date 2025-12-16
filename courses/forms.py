from django import forms
from .models import Course, Module, Lesson, CertificateSettings, Review, Assessment, Question, Choice, Submission

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'id': 'id_rating', 'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'comment': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-primary bg-white text-gray-900 placeholder-gray-400 shadow-sm', 'rows': 4, 'placeholder': 'Share your experience with this course...'}),
        }

class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['title', 'description', 'assessment_type', 'max_score', 'passing_score', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'rows': 3}),
            'assessment_type': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'max_score': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'passing_score': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'points', 'order']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'rows': 2}),
            'question_type': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'points': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'order': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
        }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'placeholder': 'Choice text'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-primary border-gray-300 dark:border-gray-600 rounded focus:ring-primary bg-gray-100 dark:bg-gray-700'}),
        }

class SubmissionGradingForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['score', 'feedback']
        widgets = {
            'score': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'feedback': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'rows': 4}),
        }

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file', 'text_content']
        widgets = {
            'text_content': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'rows': 6, 'placeholder': 'Type your answer here...'}),
        }

class CertificateSettingsForm(forms.ModelForm):
    class Meta:
        model = CertificateSettings
        fields = ['background_image', 'logo', 'signature', 'primary_color', 'secondary_color', 'accent_color', 'font_family']
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'w-full h-10 px-1 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color', 'class': 'w-full h-10 px-1 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary'}),
            'accent_color': forms.TextInput(attrs={'type': 'color', 'class': 'w-full h-10 px-1 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary'}),
            'font_family': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'category', 'description', 'price', 'thumbnail', 'level', 'has_certificate', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'level': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'has_certificate': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-primary border-gray-300 dark:border-gray-600 rounded focus:ring-primary bg-gray-100 dark:bg-gray-700'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-primary border-gray-300 dark:border-gray-600 rounded focus:ring-primary bg-gray-100 dark:bg-gray-700'}),
        }

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'order': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
        }

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'lesson_type', 'text_content', 'video_file', 'video_url', 'document_file', 'assignment_instruction', 'duration', 'is_free', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'lesson_type': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'onchange': 'toggleFields(this.value)'}),
            'text_content': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'rows': 5}),
            'video_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
            'assignment_instruction': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'rows': 3}),
            'duration': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'placeholder': 'HH:MM:SS'}),
            'is_free': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-primary border-gray-300 dark:border-gray-600 rounded focus:ring-primary bg-gray-100 dark:bg-gray-700'}),
            'order': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'}),
        }
