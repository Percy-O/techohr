from django.core.management.base import BaseCommand
from core.models import Project, Service
from django.utils.text import slugify
import uuid

class Command(BaseCommand):
    help = 'Populates slugs for Projects and Services that do not have them'

    def handle(self, *args, **options):
        self.stdout.write('Checking Projects...')
        projects = Project.objects.all()
        p_count = 0
        for project in projects:
            if not project.slug:
                project.slug = slugify(project.title)
                if not project.slug:
                     project.slug = str(uuid.uuid4())[:8]
                
                # Ensure unique
                orig_slug = project.slug
                counter = 1
                while Project.objects.filter(slug=project.slug).exclude(pk=project.pk).exists():
                    project.slug = f"{orig_slug}-{counter}"
                    counter += 1
                
                project.save()
                p_count += 1
                self.stdout.write(f'Updated slug for Project: {project.title} -> {project.slug}')
        
        self.stdout.write(f'Updated {p_count} Projects.')

        self.stdout.write('Checking Services...')
        services = Service.objects.all()
        s_count = 0
        for service in services:
            if not service.slug:
                service.slug = slugify(service.title)
                if not service.slug:
                     service.slug = str(uuid.uuid4())[:8]
                
                # Ensure unique
                orig_slug = service.slug
                counter = 1
                while Service.objects.filter(slug=service.slug).exclude(pk=service.pk).exists():
                    service.slug = f"{orig_slug}-{counter}"
                    counter += 1
                
                service.save()
                s_count += 1
                self.stdout.write(f'Updated slug for Service: {service.title} -> {service.slug}')
        
        self.stdout.write(f'Updated {s_count} Services.')
