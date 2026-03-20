from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.views.static import serve

from institute.sitemaps import CategorySitemap, PageSitemap, ServiceSitemap
from institute.views import robots_txt

sitemaps = {
    "categories": CategorySitemap,
    "services": ServiceSitemap,
    "pages": PageSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("summernote/", include("django_summernote.urls")),
    path("robots.txt", robots_txt, name="robots-txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("", include("institute.urls")),
]

# Servir les fichiers médias (images uploadées) même en production (sans Nginx/Caddy externe)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    ]
