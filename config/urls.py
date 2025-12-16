from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from users import views as user_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", user_views.admin_dashboard, name='admin_dashboard'),  # Direct access to admin dashboard
    path("", include("core.urls")),
    path("courses/", include("courses.urls")),
    path("blog/", include("blog.urls")),
    path("users/", include("users.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
