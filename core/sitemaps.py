from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Service, Project

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home', 'service_list', 'contact', 'about', 'portfolio']

    def location(self, item):
        return reverse(item)

class ServiceSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Service.objects.all()

class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Project.objects.all()
