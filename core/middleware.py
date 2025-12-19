from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from django.conf import settings
from .models import PageVisit


class PageVisitLoggerMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            if request.method != 'GET':
                return None
            path = request.path
            if path.startswith('/admin/') or path.startswith(settings.STATIC_URL) or path.startswith(settings.MEDIA_URL):
                return None
            # Avoid logging health checks or sitemap/robots
            if path in ('/sitemap.xml', '/robots.txt'):
                return None
            # Resolve to ensure valid view
            resolve(path)
            # Save visit
            PageVisit.objects.create(
                page_url=path,
                user=request.user if request.user.is_authenticated else None,
            )
        except Exception:
            # Silently ignore any logging errors
            pass
        return None

