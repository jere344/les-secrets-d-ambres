from django.contrib.sitemaps import Sitemap

from .models import Category, Service, StandalonePage


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Category.objects.published()


class ServiceSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Service.objects.published().select_related("category")


class PageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return StandalonePage.objects.published()
