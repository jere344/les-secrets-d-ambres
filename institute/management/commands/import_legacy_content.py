import re
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from institute.models import Category, Service, SiteSettings, StandalonePage, Tariff


@dataclass
class LegacyCategory:
    title: str
    url: str


LEGACY_CATEGORIES = [
    LegacyCategory("Epilation bio a Montpellier", "https://www.lessecretsdambre.com/epilation-bio-a-montpellier/"),
    LegacyCategory("Onglerie bio & soins mains et pieds", "https://www.lessecretsdambre.com/onglerie-bio-soins-mains-et-pieds-a-montpellier/"),
    LegacyCategory("Massage bio a Montpellier", "https://www.lessecretsdambre.com/massage-bio-a-montpellier/"),
    LegacyCategory("Hammam a Montpellier", "https://www.lessecretsdambre.com/hammam-a-montpellier/"),
    LegacyCategory("Soins corps bio a Montpellier", "https://www.lessecretsdambre.com/soins-corps-bio-a-montpellier/"),
    LegacyCategory("Soins visage bio a Montpellier", "https://www.lessecretsdambre.com/soins-visage-bio-a-montpellier/"),
    LegacyCategory("Black Pearl pour peaux noires", "https://www.lessecretsdambre.com/black-pearl-pour-peaux-noires/"),
    LegacyCategory("Beaute du regard", "https://www.lessecretsdambre.com/beaute-du-regard-a-montpellier/"),
    LegacyCategory("Promotions", "https://www.lessecretsdambre.com/promotions/"),
    LegacyCategory("Minceur et jambes lourdes", "https://www.lessecretsdambre.com/minceur-a-montpellier-et-jambes-lourdes/"),
    LegacyCategory("Femme enceinte et jeune maman", "https://www.lessecretsdambre.com/femme-enceinte-et-jeune-maman/"),
    LegacyCategory("Relaxation et coaching", "https://www.lessecretsdambre.com/relaxation-et-coaching/"),
    LegacyCategory("Maquillage a Montpellier", "https://www.lessecretsdambre.com/maquillage-a-montpellier/"),
    LegacyCategory("Maquillage permanent", "https://www.lessecretsdambre.com/maquillage-permanent-a-montpellier/"),
]

LEGACY_PAGES = [
    ("Blog beaute et bien etre", "blog-beaute-et-bien-etre", "https://www.lessecretsdambre.com/blog-beaute-et-bien-etre/"),
    ("Les formations", "les-formations", "https://www.lessecretsdambre.com/les-formations/"),
    ("FAQ", "faq", "https://www.lessecretsdambre.com/faq/"),
    ("A propos", "a-propos", "https://www.lessecretsdambre.com/%C3%A0-propos/"),
    ("Nous ecrire", "nous-ecrire", "https://www.lessecretsdambre.com/nous-ecrire/"),
]

PRICE_RE = re.compile(r"(\d+[\.,]?\d*)\s?€")


class Command(BaseCommand):
    help = "Import categories/pages from the legacy website and optionally extract service pricing lines."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-services",
            action="store_true",
            help="Only import categories/pages text without service extraction.",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=25,
            help="HTTP timeout in seconds.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        timeout = options["timeout"]
        extract_services = not options["skip_services"]

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/123.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "no-cache",
            }
        )

        self._ensure_site_settings()

        for index, legacy_category in enumerate(LEGACY_CATEGORIES, start=1):
            self.stdout.write(self.style.NOTICE(f"Importing category: {legacy_category.title}"))
            html = self._fetch_html(legacy_category.url, timeout)
            category = self._upsert_category(legacy_category, html, index)
            if extract_services and html:
                self._extract_services(category, html)
            self._ensure_placeholder_service(category)

        for nav_index, (title, slug, url) in enumerate(LEGACY_PAGES, start=1):
            html = self._fetch_html(url, timeout)
            summary, body_html = self._extract_text_sections(html) if html else ("", "")
            StandalonePage.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "summary": summary or f"Contenu a completer pour {title}.",
                    "body_html": body_html,
                    "show_in_nav": True,
                    "nav_order": nav_index,
                    "is_published": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("Legacy content import complete."))

    def _ensure_site_settings(self):
        SiteSettings.objects.get_or_create(
            pk=1,
            defaults={
                "brand_name": "Les secrets d'ambre",
                "tagline": "Institut de beaute bio a Montpellier - beaute & bien-etre sur mesure",
                "hero_title": "Rituels orientaux et soins naturels",
                "hero_subtitle": (
                    "L'institut propose des soins personnalises par categorie, "
                    "avec diagnostic, expertise et produits naturels."
                ),
                "contact_phone": "+33662360108",
                "contact_phone_display": "06 62 36 01 08",
                "address_line": "17 rue Lunaret",
                "postal_code_city": "34090 Montpellier",
                "opening_hours": "Du lundi au samedi sur rendez-vous",
                "booking_label": "Prendre rendez-vous",
                "booking_url": "https://www.planity.com/les-secrets-dambre-epilation-miel-bio-caramel-orientale-soin-peaux-noires-34090-montpellier",
                "instagram_url": "https://www.instagram.com/lessecretsdambre/",
                "facebook_url": "https://www.facebook.com/LesSecretsDAmbre/",
                "seo_description": "Institut de beaute bio a Montpellier. Soins orientaux, massages, hammam, visage, corps et epilation naturelle.",
            },
        )

    def _fetch_html(self, url, timeout):
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            self.stdout.write(self.style.WARNING(f"Failed to fetch {url}: {exc}"))
            return None

    def _upsert_category(self, legacy_category, html, display_order):
        if html:
            summary, body_html = self._extract_text_sections(html)
        else:
            summary, body_html = ("", "")

        category, _ = Category.objects.update_or_create(
            slug=slugify(legacy_category.title),
            defaults={
                "title": legacy_category.title,
                "short_intro": summary or f"Contenu a completer pour {legacy_category.title}.",
                "body_html": body_html,
                "legacy_url": legacy_category.url,
                "display_order": display_order,
                "is_published": True,
                "seo_title": legacy_category.title,
                "seo_description": (summary[:160] if summary else legacy_category.title[:160]),
            },
        )
        return category

    def _extract_text_sections(self, html):
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            tag.decompose()

        chunks = []
        for node in soup.find_all(["h1", "h2", "h3", "p", "li", "img"]):
            if node.name == "img" and node.get("src"):
                src = node.get("src")
                alt = node.get("alt", "")
                chunks.append(f'<p><img src="{src}" alt="{alt}"></p>')
                continue

            text = " ".join(node.get_text(" ", strip=True).split())
            if not text:
                continue
            if len(text) < 22:
                continue
            if "PLANITY" in text or "Connexion" in text or "Institut Bio Montpellier" in text:
                continue

            tag_name = "p" if node.name == "li" else node.name
            chunks.append(f"<{tag_name}>{text}</{tag_name}>")

        if not chunks:
            return "", ""

        summary_text = BeautifulSoup("".join(chunks[:4]), "html.parser").get_text(" ", strip=True)
        summary = summary_text[:280]
        body_html = "\n".join(chunks[:30])
        return summary, body_html

    def _extract_services(self, category, html):
        soup = BeautifulSoup(html, "html.parser")
        text_lines = [
            " ".join(line.split())
            for line in soup.get_text("\n").splitlines()
            if line.strip()
        ]

        parsed = []
        for idx, line in enumerate(text_lines):
            if not PRICE_RE.search(line):
                continue
            if "€" not in line:
                continue

            prev = text_lines[idx - 1] if idx > 0 else ""
            name = prev
            if len(name) < 4 or PRICE_RE.search(name):
                name = line.split("€", 1)[0]
            name = name.strip(" -:\t")

            if len(name) < 4:
                continue
            price_match = PRICE_RE.findall(line)
            if not price_match:
                continue

            price_label = line
            price_from = self._safe_price(price_match[0])
            price_to = self._safe_price(price_match[-1]) if len(price_match) > 1 else None
            parsed.append((name[:170], price_label[:80], price_from, price_to))

        seen = set()
        for order, (name, price_label, price_from, price_to) in enumerate(parsed, start=1):
            slug = slugify(name)[:170]
            unique_key = (slug, price_label)
            if unique_key in seen:
                continue
            seen.add(unique_key)

            service, _ = Service.objects.update_or_create(
                category=category,
                slug=slug,
                defaults={
                    "name": name,
                    "short_description": "Soin importe automatiquement depuis le site historique.",
                    "display_order": order,
                    "is_published": True,
                },
            )

            Tariff.objects.update_or_create(
                service=service,
                label="Tarif principal",
                defaults={
                    "duration_text": "A preciser",
                    "price_label": price_label,
                    "price_from": price_from,
                    "price_to": price_to,
                    "display_order": 1,
                    "is_published": True,
                },
            )

    def _safe_price(self, raw_value):
        try:
            return Decimal(raw_value.replace(",", "."))
        except InvalidOperation:
            return None

    def _ensure_placeholder_service(self, category):
        if category.services.exists() and Tariff.objects.filter(service__category=category).exists():
            return

        service, _ = Service.objects.update_or_create(
            category=category,
            slug="offre-a-completer",
            defaults={
                "name": "Offre a completer",
                "short_description": "Service importe automatiquement. Remplacez ce contenu.",
                "display_order": 1,
                "is_published": True,
            },
        )

        Tariff.objects.update_or_create(
            service=service,
            label="Tarif a renseigner",
            defaults={
                "duration_text": "A renseigner",
                "price_label": "Tarif a renseigner",
                "display_order": 1,
                "is_published": True,
            },
        )
