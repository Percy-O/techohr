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
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)

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

# --- Site Settings & Company ---

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=200, default='TechOhr')
    logo = models.ImageField(upload_to='settings/logo/', blank=True, null=True)
    favicon = models.ImageField(upload_to='settings/favicon/', blank=True, null=True)
    logo_light = models.ImageField(upload_to='settings/logo/', blank=True, null=True)
    logo_dark = models.ImageField(upload_to='settings/logo/', blank=True, null=True)

    # Contact Info
    address = models.CharField(max_length=255, blank=True)
    email_primary = models.EmailField(blank=True)
    email_support = models.EmailField(blank=True)
    phone_primary = models.CharField(max_length=50, blank=True)

    # Social Links
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)

    # Map Embed (Google Maps iframe src)
    map_embed_url = models.URLField(blank=True, help_text="Paste the Google Maps embed URL")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Site Settings"

class CompanyStats(models.Model):
    projects_completed = models.PositiveIntegerField(default=0)
    happy_clients = models.PositiveIntegerField(default=0)
    team_members = models.PositiveIntegerField(default=0)
    experience_years = models.PositiveIntegerField(default=3)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Company Stats"

class Employee(models.Model):
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    photo = models.ImageField(upload_to='employees/photos/', blank=True, null=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']


class PageVisit(models.Model):
    page_url = models.CharField(max_length=255)
    visited_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        who = self.user.username if self.user else 'Anonymous'
        return f"{who} visited {self.page_url} at {self.visited_at}"

    def __str__(self):
        return f"{self.name} - {self.role}"
