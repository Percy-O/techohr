from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate
import os


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        def sync_site(sender, **kwargs):
            try:
                from django.contrib.sites.models import Site
                site_id = getattr(settings, 'SITE_ID', 1)
                default_domain = 'localhost'
                if not settings.DEBUG:
                    default_domain = 'techohr.com'
                env_domain = os.getenv('CANONICAL_DOMAIN') or os.getenv('SITE_DOMAIN')
                domain = env_domain or default_domain
                name = os.getenv('SITE_NAME') or 'TechOhr'
                site, _ = Site.objects.get_or_create(id=site_id, defaults={'domain': domain, 'name': name})
                if site.domain != domain or site.name != name:
                    site.domain = domain
                    site.name = name
                    site.save()
            except Exception:
                pass

        post_migrate.connect(sync_site, sender=self)
