from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic.base import TemplateView

from users import views as user_views
from core.sitemaps import StaticViewSitemap, ServiceSitemap, ProjectSitemap
from courses.sitemaps import CourseSitemap
from blog.sitemaps import PostSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'services': ServiceSitemap,
    'projects': ProjectSitemap,
    'courses': CourseSitemap,
    'posts': PostSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", user_views.admin_dashboard, name='admin_dashboard'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("", include("core.urls")),
    path("courses/", include("courses.urls")),
    path("blog/", include("blog.urls")),
    path("users/", include("users.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
