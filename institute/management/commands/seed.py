from django.core.management.base import BaseCommand
from django.db import transaction

from institute.models import (
    Category,
    Certification,
    HomeFlexibleSection,
    Partner,
    RitualPoint,
    Service,
    SiteSettings,
    StandalonePage,
    Tariff,
    Testimonial,
)

from .seed_data import (
    CATEGORY_SEED,
    PAGE_SEED,
    PARTNER_SEED,
    RITUAL_POINT_SEED,
    TESTIMONIAL_SEED,
    CERTIFICATION_SEED
)

class Command(BaseCommand):
    help = "Seed data from old website into database."

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Clear existing data before seeding')

    def handle(self, *args, **options):
        with transaction.atomic():
            if options.get('reset'):
                self.stdout.write("Clearing existing data...")
                Category.objects.all().delete()
                Service.objects.all().delete()
                Tariff.objects.all().delete()
                Partner.objects.all().delete()
                RitualPoint.objects.all().delete()
                Testimonial.objects.all().delete()
                Certification.objects.all().delete()
                StandalonePage.objects.all().delete()

            self.stdout.write("Seeding categories and services...")
            for idx, cat_data in enumerate(CATEGORY_SEED):
                cat, _ = Category.objects.update_or_create(
                    slug=cat_data["slug"],
                    defaults={
                        "title": cat_data.get("title", ""),
                        "intro": cat_data.get("intro", ""),
                        "body": cat_data.get("body", ""),
                        "display_order": idx * 10,
                        "is_published": True
                    }
                )
                for s_idx, srv_data in enumerate(cat_data.get("services", [])):
                    srv, _ = Service.objects.update_or_create(
                        slug=srv_data["slug"],
                        defaults={
                            "category": cat,
                            "name": srv_data.get("name", ""),
                            "summary": srv_data.get("summary", ""),
                            "details": srv_data.get("details", ""),
                            "featured": srv_data.get("featured", False),
                            "display_order": s_idx * 10,
                            "is_published": True
                        }
                    )
                    for t_idx, tr_data in enumerate(srv_data.get("tariffs", [])):
                        Tariff.objects.update_or_create(
                            service=srv,
                            label=tr_data["label"],
                            defaults={
                                "price_label": tr_data.get("price", ""),
                                "promo_price_label": tr_data.get("promo", ""),
                                "notes": tr_data.get("notes", ""),
                                "display_order": t_idx * 10,
                                "is_published": True
                            }
                        )

            self.stdout.write("Seeding pages...")
            for idx, page in enumerate(PAGE_SEED):
                StandalonePage.objects.update_or_create(
                    slug=page["slug"],
                    defaults={
                        "title": page.get("title", ""),
                        "body_html": page.get("body_html", ""),
                        "is_published": True,
                        "show_in_nav": True,
                        "nav_order": idx * 10
                    }
                )
            
            self.stdout.write("Seeding partners...")
            for idx, p in enumerate(PARTNER_SEED):
                Partner.objects.update_or_create(
                    slug=p["slug"],
                    defaults={
                        "name": p.get("name", ""),
                        "website_url": p.get("website_url", ""),
                        "external_image_url": p.get("external_image_url", ""),
                        "display_order": idx * 10,
                        "is_published": True
                    }
                )

            self.stdout.write("Seeding ritual points...")
            for idx, r in enumerate(RITUAL_POINT_SEED):
                RitualPoint.objects.update_or_create(
                    title=r.get("title", ""),
                    defaults={
                        "text": r.get("text", ""),
                        "icon_class": r.get("icon_class", ""),
                        "display_order": idx * 10,
                        "is_published": True
                    }
                )

            self.stdout.write("Seeding testimonials...")
            for idx, t in enumerate(TESTIMONIAL_SEED):
                Testimonial.objects.update_or_create(
                    author_name=t.get("author_name", ""),
                    defaults={
                        "content": t.get("content", ""),
                        "display_order": idx * 10,
                        "is_published": True
                    }
                )

            self.stdout.write("Seeding certifications...")
            for idx, c in enumerate(CERTIFICATION_SEED):
                Certification.objects.update_or_create(
                    slug=c["slug"],
                    defaults={
                        "name": c.get("name", ""),
                        "description": c.get("description", ""),
                        "website_url": c.get("website_url", ""),
                        "external_image_url": c.get("external_image_url", ""),
                        "display_order": idx * 10,
                        "is_published": True
                    }
                )
            
            self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
