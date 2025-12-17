from django.db import models
from django.utils.text import slugify
from django.urls import reverse
import uuid

class Service(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=100, help_text="FontAwesome or Heroicon class", blank=True)
    short_description = models.TextField(help_text="For list view")
    content = models.TextField(help_text="Detailed content")
    features = models.TextField(help_text="Comma-separated list of features", blank=True)
    technologies = models.CharField(max_length=500, help_text="Comma-separated technologies", blank=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            if not self.slug:
                 self.slug = str(uuid.uuid4())[:8]
            orig_slug = self.slug
            counter = 1
            while Service.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{orig_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('service_detail', kwargs={'slug': self.slug})

class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='projects/')
    description = models.TextField()
    client = models.CharField(max_length=200, blank=True)
    url = models.URLField(blank=True)
    technologies = models.CharField(max_length=500)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            if not self.slug:
                 self.slug = str(uuid.uuid4())[:8]
            orig_slug = self.slug
            counter = 1
            while Project.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{orig_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'slug': self.slug})

class Testimonial(models.Model):
    client_name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    rating = models.IntegerField(default=5)

    def __str__(self):
        return f"{self.client_name} - {self.company}"

class Contact(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email
