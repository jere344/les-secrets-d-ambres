from django.db.utils import OperationalError, ProgrammingError

from .models import Category, SiteSettings, StandalonePage


def global_context(_request):
    try:
        settings_obj = SiteSettings.get_solo()
        nav_categories = Category.objects.published()
        nav_pages = StandalonePage.objects.published().filter(show_in_nav=True)
        footer_pages = StandalonePage.objects.published().filter(
            slug__in=["mentions-legales"]
        )
    except (OperationalError, ProgrammingError):
        settings_obj = None
        nav_categories = []
        nav_pages = []
        footer_pages = []

    return {
        "site_settings": settings_obj,
        "nav_categories": nav_categories,
        "nav_pages": nav_pages,
        "footer_pages": footer_pages,
    }
