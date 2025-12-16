from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=100, blank=True, help_text="Icon class")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Course(models.Model):
    LEVEL_CHOICES = (
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    thumbnail = models.ImageField(upload_to='courses/thumbnails/')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Beginner')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    
    # Certificate Settings
    has_certificate = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            if not self.slug:
                 self.slug = str(uuid.uuid4())[:8]
            # Ensure unique
            orig_slug = self.slug
            counter = 1
            while Course.objects.filter(slug=self.slug).exists():
                self.slug = f"{orig_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    def get_duration(self):
        # Calculate total duration from lessons
        total = sum([l.duration for m in self.modules.all() for l in m.lessons.all() if l.duration], start=timedelta(0))
        return total

class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    LESSON_TYPE_CHOICES = (
        ('video', 'Video'),
        ('article', 'Article/Text'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('document', 'Document (PDF/PPT)'),
    )
    
    module = models.ForeignKey(Module, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default='video')
    
    # Content Fields
    text_content = models.TextField(blank=True, help_text="For Articles or Video Descriptions")
    
    # Video Fields
    video_file = models.FileField(upload_to='courses/videos/', blank=True, null=True, help_text="Upload video file directly")
    video_url = models.URLField(blank=True, help_text="YouTube/Vimeo URL (if not uploading)")
    
    # Document Fields
    document_file = models.FileField(upload_to='courses/documents/', blank=True, null=True, help_text="PDF, PPT, or other files")
    
    # Assignment Fields
    assignment_instruction = models.TextField(blank=True, help_text="Instructions for the assignment")
    
    duration = models.DurationField(null=True, blank=True, help_text="Duration of the lesson")
    is_free = models.BooleanField(default=False, help_text="Preview available without enrollment")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            if not self.slug:
                 self.slug = str(uuid.uuid4())[:8]
            # Ensure unique within module or course? 
            # Ideally unique within course, but unique=True is not set on model field so it's not enforced at DB level globally.
            # But url patterns usually require unique slug per course or globally if only slug is used.
            # Here url is /courses/<course_slug>/learn/<lesson_slug>/
            # So lesson slug needs to be unique within the course.
            
            # Let's just make it unique-ish
            orig_slug = self.slug
            counter = 1
            while Lesson.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{orig_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"
    
    def get_progress(self):
        total_lessons = Lesson.objects.filter(module__course=self.course).count()
        if total_lessons == 0:
            return 0
        completed = LessonCompletion.objects.filter(enrollment=self, is_completed=True).count()
        return int((completed / total_lessons) * 100)

class LessonCompletion(models.Model):
    enrollment = models.ForeignKey(Enrollment, related_name='completions', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('enrollment', 'lesson')

class Certificate(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='certificates', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='certificates', on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    file = models.FileField(upload_to='certificates/', blank=True, null=True)

    def __str__(self):
        return f"Certificate for {self.student} - {self.course}"

class CertificateSettings(models.Model):
    # Only one instance should exist, or one per site if multi-tenant, but assuming single site for now.
    # We can enforce singleton pattern or just allow editing the latest one.
    
    background_image = models.ImageField(upload_to='certificates/backgrounds/', blank=True, null=True, help_text="Upload a background image for the certificate.")
    logo = models.ImageField(upload_to='certificates/logos/', blank=True, null=True, help_text="Upload a logo to appear on the certificate.")
    signature = models.ImageField(upload_to='certificates/signatures/', blank=True, null=True, help_text="Upload a signature image.")
    
    primary_color = models.CharField(max_length=7, default='#1a202c', help_text="Primary text color (Hex code, e.g., #000000)")
    secondary_color = models.CharField(max_length=7, default='#4a5568', help_text="Secondary text color (Hex code, e.g., #555555)")
    accent_color = models.CharField(max_length=7, default='#3182ce', help_text="Accent color for borders/lines (Hex code)")
    
    font_family = models.CharField(max_length=50, choices=[
        ('Helvetica', 'Helvetica'), 
        ('Times', 'Times'), 
        ('Courier', 'Courier'),
        ('GreatVibes', 'Great Vibes (Script)'),
        ('Lato', 'Lato (Modern Sans)')
    ], default='Helvetica', help_text="Font family for the certificate.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk and CertificateSettings.objects.exists():
            # If you want to ensure only one exists, you can raise an error or just update the existing one.
            pass
        return super(CertificateSettings, self).save(*args, **kwargs)

    def __str__(self):
        return "Certificate Design Settings"
    
    class Meta:
        verbose_name = "Certificate Design"
        verbose_name_plural = "Certificate Designs"

class Review(models.Model):
    course = models.ForeignKey(Course, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.course} ({self.rating})"

class Assessment(models.Model):
    ASSESSMENT_TYPES = (
        ('assignment', 'Assignment (File/Text)'),
        ('quiz', 'Quiz (Multiple Choice/Text)'),
    )
    course = models.ForeignKey(Course, related_name='assessments', on_delete=models.CASCADE)
    module = models.ForeignKey(Module, related_name='assessments', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES, default='quiz')
    
    # Grading
    max_score = models.PositiveIntegerField(default=100)
    passing_score = models.PositiveIntegerField(default=60)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_assessment_type_display()})"

class Question(models.Model):
    QUESTION_TYPES = (
        ('single_choice', 'Single Choice'),
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('text', 'Short Answer'),
    )
    assessment = models.ForeignKey(Assessment, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='single_choice')
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text[:50]

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.text

class Submission(models.Model):
    assessment = models.ForeignKey(Assessment, related_name='submissions', on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='submissions', on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # For Assignments
    file = models.FileField(upload_to='assignments/submissions/', blank=True, null=True)
    text_content = models.TextField(blank=True)
    
    # Grading
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    graded_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='graded_submissions', on_delete=models.SET_NULL, null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('assessment', 'student')

    def __str__(self):
        return f"Submission for {self.assessment} by {self.student}"

class StudentAnswer(models.Model):
    submission = models.ForeignKey(Submission, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    points_awarded = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Answer to {self.question} in {self.submission}"
