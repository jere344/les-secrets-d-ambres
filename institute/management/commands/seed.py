import datetime
import json
import re
import gzip
import unicodedata
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.html import escape
from django.utils.text import slugify

from institute.models import (
    BlogPost,
    Category,
    Service,
    StandalonePage,
    Tag,
    Tariff,
)

from .seed_maps import (
    CATEGORY_CONTENT_ASSIGNMENTS,
    CATEGORY_CONTENT_OVERRIDES,
    CATEGORY_DEFINITIONS,
    CATEGORY_PRIMARY_COVER_IMAGE,
    BLOG_POST_DEFINITIONS,
    LEGACY_ACHAT_TO_SERVICE,
    LEGACY_STANDALONE_SLUG_MAP,
    LEGACY_TOPLEVEL_TO_CATEGORY,
    LEGACY_TOPLEVEL_TO_SERVICE,
    SERVICE_CONTENT_ASSIGNMENTS,
    SERVICE_CONTENT_OVERRIDES,
    SERVICE_PRIMARY_IMAGE,
    SERVICE_DEFINITIONS,
    SERVICE_TARIFF_OVERRIDES,
    STANDALONE_PAGE_DEFINITIONS,
)

LEGACY_CHUNKS_JSON_PATH = Path(__file__).parent / "seed_maps" / "legacy_chunks.json"
TARIFF_AI_JSON_PATH = Path(__file__).parent / "seed_maps" / "tariff_ai_extracted.json"
TARIFF_TEXT_JSON_PATH = Path(__file__).parent / "seed_maps" / "tariff_text_extracted.json"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
LEGACY_MIRROR_ROOT = PROJECT_ROOT / "scripts" / "ambre" / "www.lessecretsdambre.com"


class Command(BaseCommand):
    help = "Seed database from manual dictionaries and chunk catalog only."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ai_tariff_overrides_cache = None

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Clear existing data before seeding")

    def handle(self, *args, **options):
        with transaction.atomic():
            if options.get("reset"):
                self._reset_tables()

            chunk_catalog = self._load_chunk_catalog()
            self._seed_manual_categories(chunk_catalog)
            self._seed_manual_services(chunk_catalog)
            self._seed_manual_standalone_pages()
            self._seed_manual_blog_posts()

            self.stdout.write(self.style.SUCCESS("Database seeded successfully from manual dictionaries."))

    def _reset_tables(self):
        self.stdout.write("Clearing existing data...")
        from institute.models import GalleryImage
        GalleryImage.objects.all().delete()
        BlogPost.objects.all().delete()
        Tag.objects.all().delete()
        StandalonePage.objects.all().delete()
        Tariff.objects.all().delete()
        Service.objects.all().delete()
        Category.objects.all().delete()

    def _load_chunk_catalog(self):
        if not LEGACY_CHUNKS_JSON_PATH.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Legacy chunk catalog not found: {LEGACY_CHUNKS_JSON_PATH}. "
                    "Run build_legacy_chunks to generate it."
                )
            )
            return {}

        try:
            payload = json.loads(LEGACY_CHUNKS_JSON_PATH.read_text(encoding="utf-8"))
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"Failed to load chunk catalog: {exc}"))
            return {}

        loaded_sources = len(payload.get("source_pages", {}))
        loaded_chunks = len(payload.get("chunk_index", {}))
        self.stdout.write(f"Loaded chunk catalog: {loaded_sources} sources, {loaded_chunks} chunks")
        return payload

    def _seed_manual_categories(self, chunk_catalog):
        imported = 0
        for idx, category_def in enumerate(CATEGORY_DEFINITIONS):
            slug = category_def["slug"]
            override = CATEGORY_CONTENT_OVERRIDES.get(slug, {})
            assignment = CATEGORY_CONTENT_ASSIGNMENTS.get(slug, {})

            chunk_html, chunk_meta = self._render_assigned_content(chunk_catalog, assignment)
            body_html = self._join_html_blocks(override.get("body_html", ""), chunk_html)
            short_intro = override.get("short_intro") or self._first_chunk_preview(chunk_meta)
            legacy_url = self._pick_legacy_url(chunk_catalog, assignment)

            Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": category_def["title"],
                    "short_intro": short_intro,
                    "body_html": body_html,
                    "legacy_url": legacy_url,
                    "cover_image": CATEGORY_PRIMARY_COVER_IMAGE.get(slug, ""),
                    "display_order": idx * 10,
                    "is_published": True,
                },
            )
            imported += 1

        self.stdout.write(f"Imported categories: {imported}")

    def _seed_manual_services(self, chunk_catalog):
        imported = 0
        for idx, service_def in enumerate(SERVICE_DEFINITIONS):
            category = Category.objects.filter(slug=service_def["category"]).first()
            if not category:
                self.stdout.write(self.style.WARNING(f"Missing category for service: {service_def['slug']}"))
                continue

            slug = service_def["slug"]
            tariff_rows = self._get_merged_tariff_rows(slug)
            if not tariff_rows:
                tariff_rows = [
                    {"label": "Diagnostic personnalise", "price_label": "Tarif sur demande", "notes": ""},
                    {"label": "Programme sur mesure", "price_label": "Sur devis", "notes": ""},
                ]

            override = SERVICE_CONTENT_OVERRIDES.get(slug, {})
            assignment = SERVICE_CONTENT_ASSIGNMENTS.get(slug, {})

            chunk_html, chunk_meta = self._render_assigned_content(chunk_catalog, assignment)
            details_html = self._join_html_blocks(override.get("details_html", ""), chunk_html)
            short_description = override.get("short_description") or self._first_chunk_preview(chunk_meta)

            service, _ = Service.objects.update_or_create(
                category=category,
                slug=slug,
                defaults={
                    "name": service_def["title"],
                    "short_description": short_description,
                    "details_html": details_html,
                    "image": SERVICE_PRIMARY_IMAGE.get(slug)
                    or CATEGORY_PRIMARY_COVER_IMAGE.get(service_def["category"], ""),
                    "display_order": idx * 10,
                    "is_featured": bool(service_def.get("featured", False)),
                    "is_published": True,
                },
            )

            Tariff.objects.filter(service=service).delete()

            for tariff_idx, row in enumerate(tariff_rows):
                notes_text = str(row.get("notes", "")).strip()

                details_html = str(row.get("details_html", "")).strip()
                if not details_html:
                    details_html = self._notes_to_details_html(notes_text)

                Tariff.objects.create(
                    service=service,
                    label=str(row.get("label", "Option"))[:140],
                    duration_text=str(row.get("duration_text", ""))[:80],
                    price_label=str(row.get("price_label", "Tarif sur demande"))[:80],
                    promo_price_label=str(row.get("promo_price_label", ""))[:80],
                    notes=notes_text[:2000],
                    details_html=details_html[:6000],
                    display_order=tariff_idx * 10,
                    is_published=True,
                )

            imported += 1

        self.stdout.write(f"Imported services: {imported}")

    def _render_assigned_content(self, chunk_catalog, assignment):
        if not chunk_catalog:
            return "", []

        source_pages = chunk_catalog.get("source_pages", {})
        chunk_index = chunk_catalog.get("chunk_index", {})

        chunk_meta = []
        seen_ids = set()

        for chunk_id in assignment.get("chunk_ids", []):
            payload = chunk_index.get(chunk_id)
            if not payload:
                self.stdout.write(self.style.WARNING(f"Unknown chunk id: {chunk_id}"))
                continue
            seen_ids.add(chunk_id)
            chunk_meta.append(
                {
                    "id": chunk_id,
                    "source_ref": payload.get("source_ref", ""),
                    "title": payload.get("title", ""),
                    "html": payload.get("html", ""),
                    "text_preview": payload.get("text_preview", ""),
                }
            )

        for source_ref in assignment.get("source_refs", []):
            source_payload = source_pages.get(source_ref)
            if not source_payload:
                self.stdout.write(self.style.WARNING(f"Unknown source ref: {source_ref}"))
                continue

            for chunk in source_payload.get("chunks", []):
                chunk_id = chunk.get("id")
                if not chunk_id or chunk_id in seen_ids:
                    continue
                seen_ids.add(chunk_id)
                chunk_meta.append(
                    {
                        "id": chunk_id,
                        "source_ref": source_ref,
                        "title": chunk.get("title", ""),
                        "html": chunk.get("html", ""),
                        "text_preview": chunk.get("text_preview", ""),
                    }
                )

        html_parts = [
            self._normalize_imported_html(item["html"])
            for item in chunk_meta
            if item.get("html")
        ]
        return "\n".join(html_parts), chunk_meta

    def _pick_legacy_url(self, chunk_catalog, assignment):
        source_pages = chunk_catalog.get("source_pages", {}) if chunk_catalog else {}
        for source_ref in assignment.get("source_refs", []):
            source_payload = source_pages.get(source_ref)
            if source_payload and source_payload.get("legacy_url"):
                return source_payload["legacy_url"]
        return ""

    def _first_chunk_preview(self, chunk_meta):
        for item in chunk_meta:
            preview = str(item.get("text_preview", "")).strip()
            if len(preview) >= 40:
                return preview[:800]
        return ""

    def _join_html_blocks(self, *blocks):
        clean_blocks = [str(block).strip() for block in blocks if str(block).strip()]
        return "\n".join(clean_blocks)

    def _normalize_text(self, value):
        text = str(value or "").lower().replace("\xa0", " ")
        text = unicodedata.normalize("NFKD", text)
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"[^a-z0-9àâäçéèêëîïôöùûüÿæœ\- ]+", "", text)
        return text

    def _notes_to_details_html(self, notes_text):
        raw = str(notes_text or "").strip()
        if not raw:
            return ""

        blocks = [block.strip() for block in re.split(r"\n\s*\n", raw) if block.strip()]
        html_blocks = []
        for block in blocks:
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue
            escaped = "<br/>".join(escape(line) for line in lines)
            html_blocks.append(f"<p>{escaped}</p>")

        return "".join(html_blocks)

    def _get_merged_tariff_rows(self, service_slug):
        base_rows = list(SERVICE_TARIFF_OVERRIDES.get(service_slug, []))
        ai_rows = list(self._load_ai_tariff_overrides().get(service_slug, []))
        if ai_rows:
            return ai_rows

        text_rows = list(self._load_text_tariff_overrides().get(service_slug, []))
        if not text_rows:
            return base_rows

        merged_rows = []
        index_by_key = {}

        def _row_key(row):
            label = self._normalize_text(row.get("label", ""))
            price = self._normalize_text(row.get("price_label", ""))
            return f"{label}::{price}"

        for row in base_rows:
            row_copy = dict(row)
            key = _row_key(row_copy)
            if key not in index_by_key:
                index_by_key[key] = len(merged_rows)
                merged_rows.append(row_copy)

        for row in text_rows:
            row_copy = dict(row)
            key = _row_key(row_copy)
            if key in index_by_key:
                existing = merged_rows[index_by_key[key]]
                new_notes = str(row_copy.get("notes", "")).strip()
                if new_notes:
                    existing["notes"] = new_notes
                new_details_html = str(row_copy.get("details_html", "")).strip()
                if new_details_html:
                    existing["details_html"] = new_details_html
                new_duration = str(row_copy.get("duration_text", "")).strip()
                if new_duration:
                    existing["duration_text"] = new_duration
            else:
                index_by_key[key] = len(merged_rows)
                merged_rows.append(row_copy)

        return merged_rows

    def _load_ai_tariff_overrides(self):
        if self._ai_tariff_overrides_cache is not None:
            return self._ai_tariff_overrides_cache

        if not TARIFF_AI_JSON_PATH.exists():
            self._ai_tariff_overrides_cache = {}
            return self._ai_tariff_overrides_cache

        try:
            payload = json.loads(TARIFF_AI_JSON_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                self._ai_tariff_overrides_cache = payload
            else:
                self._ai_tariff_overrides_cache = {}
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"Failed to load AI tariff overrides: {exc}"))
            self._ai_tariff_overrides_cache = {}

        return self._ai_tariff_overrides_cache

    def _load_text_tariff_overrides(self):
        if not TARIFF_TEXT_JSON_PATH.exists():
            return {}

        try:
            payload = json.loads(TARIFF_TEXT_JSON_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"Failed to load text tariff overrides: {exc}"))
        return {}

    def _seed_manual_standalone_pages(self):
        imported = 0
        for page_def in STANDALONE_PAGE_DEFINITIONS:
            legacy_payload = self._extract_legacy_payload(page_def.get("legacy_url", ""))

            title = page_def.get("title") or legacy_payload.get("title") or page_def["slug"].replace("-", " ").title()
            summary = (page_def.get("summary") or legacy_payload.get("summary") or "").strip()
            body_html = (page_def.get("body_html") or legacy_payload.get("content_html") or "").strip()
            if not body_html:
                body_html = (
                    "<p>Contenu en cours de migration depuis l'ancien site.</p>"
                    f"<p><a href=\"{page_def.get('legacy_url', '')}\" rel=\"noopener\" target=\"_blank\">Voir la version historique</a></p>"
                )

            summary = self._compact_summary(summary, body_html, max_len=280)

            if page_def["slug"] in ["galerie-photos-1", "galerie-photos-2"]:
                from bs4 import BeautifulSoup
                from institute.models import GalleryImage
                soup = BeautifulSoup(body_html, "html.parser")
                for img in soup.find_all("img"):
                    src = img.get("src", "")
                    if src and not src.startswith("data:"):
                        GalleryImage.objects.create(
                            title=(img.get("alt") or "")[:140],
                            external_image_url=src,
                            display_order=imported * 10
                        )
                continue

            StandalonePage.objects.update_or_create(
                slug=page_def["slug"],
                defaults={
                    "title": title[:180],
                    "summary": summary[:4000],
                    "body_html": body_html,
                    "show_in_nav": bool(page_def.get("show_in_nav", True)),
                    "nav_order": int(page_def.get("nav_order", imported * 10)),
                    "is_published": True,
                    "seo_title": title[:70],
                    "seo_description": summary[:160],
                    "seo_keywords": page_def.get("seo_keywords", "")[:255],
                },
            )
            imported += 1

        self.stdout.write(f"Imported standalone pages: {imported}")

    def _seed_manual_blog_posts(self):
        imported = 0
        for post_def in BLOG_POST_DEFINITIONS:
            legacy_payload = self._extract_legacy_payload(post_def.get("legacy_url", ""))

            title = (
                post_def.get("title")
                or legacy_payload.get("title")
                or post_def["slug"].replace("-", " ").title()
            ).strip()
            summary = (post_def.get("summary") or legacy_payload.get("summary") or "").strip()
            content = (post_def.get("content") or legacy_payload.get("content_html") or "").strip()
            if not content:
                content = (
                    "<p>Contenu en cours de migration depuis le site historique.</p>"
                    f"<p><a href=\"{post_def.get('legacy_url', '')}\" rel=\"noopener\" target=\"_blank\">Consulter l'article d'origine</a></p>"
                )

            if not summary:
                summary = self._extract_text_preview(content)

            post, _ = BlogPost.objects.update_or_create(
                slug=post_def["slug"],
                defaults={
                    "title": title[:200],
                    "summary": summary[:5000],
                    "content": content,
                    "image": post_def.get("image") or legacy_payload.get("image_path", ""),
                    "is_published": True,
                    "created_at": self._extract_date_from_legacy_url(post_def.get("legacy_url", "")) or datetime.datetime.now(),
                },
            )

            tag_names = post_def.get("tags") or legacy_payload.get("tags") or ["Bien-etre"]
            tag_objects = []
            for tag_name in tag_names:
                clean_name = str(tag_name).strip()
                if not clean_name:
                    continue
                tag_slug = slugify(clean_name)[:50] or f"tag-{imported}"
                tag_obj, _ = Tag.objects.get_or_create(
                    slug=tag_slug,
                    defaults={"name": clean_name[:50]},
                )
                tag_objects.append(tag_obj)

            post.tags.set(tag_objects)
            imported += 1

        self.stdout.write(f"Imported blog posts: {imported}")

    def _extract_date_from_legacy_url(self, legacy_url):
        #  # use the date in the legacy_url (like  "https://www.lessecretsdambre.com/2025/05/16/..." => created_at = 2025-05-16)
        if not legacy_url:
            return None
        parsed = urlparse(legacy_url)
        match = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", parsed.path)
        if match:
            try:
                year, month, day = map(int, match.groups())
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None
        return None

    def _extract_legacy_payload(self, legacy_url):
        payload = {
            "title": "",
            "summary": "",
            "content_html": "",
            "tags": [],
            "image_path": "",
        }
        html_path = self._resolve_legacy_html_path(legacy_url)
        if not html_path:
            return payload

        try:
            raw_bytes = html_path.read_bytes()
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"Failed reading legacy file {html_path}: {exc}"))
            return payload

        html_text = self._decode_legacy_html(raw_bytes)
        if not html_text:
            self.stdout.write(self.style.WARNING(f"Failed decoding legacy HTML: {html_path}"))
            return payload

        soup = BeautifulSoup(html_text, "html.parser")
        payload["title"] = self._extract_meta_content(
            soup,
            [
                ("meta", {"name": "twitter:title"}),
                ("meta", {"property": "og:title"}),
            ],
        )

        if not payload["title"] and soup.title:
            payload["title"] = soup.title.get_text(" ", strip=True).split(" - ")[0].strip()

        payload["summary"] = self._extract_meta_content(
            soup,
            [
                ("meta", {"name": "twitter:description"}),
                ("meta", {"property": "og:description"}),
                ("meta", {"name": "description"}),
            ],
        )

        payload["tags"] = [
            item.get("content", "").strip()
            for item in soup.select('meta[property="article:tag"]')
            if item.get("content", "").strip()
        ]

        content_area = self._select_main_content_node(soup)
        if content_area:
            for node in content_area.select("#content_start, script, style, noscript, .j-comment"):
                node.decompose()
            for node in content_area.select('[id*="comment"], .skiptoform, .j-blog-comment-counter'):
                node.decompose()

            payload["content_html"] = self._normalize_imported_html(str(content_area).strip())

            payload["image_path"] = self._pick_best_legacy_image_path(content_area)

        if not payload["summary"] and payload["content_html"]:
            payload["summary"] = self._extract_text_preview(payload["content_html"])

        return payload

    def _resolve_legacy_html_path(self, legacy_url):
        if not legacy_url:
            return None

        parsed = urlparse(legacy_url)
        raw_path = unquote(parsed.path).strip("/")
        candidates = []

        if raw_path:
            candidates.append(LEGACY_MIRROR_ROOT / raw_path / "index.html")
            candidates.append(LEGACY_MIRROR_ROOT / raw_path)

            mojibake_path = raw_path.encode("utf-8", errors="ignore").decode("latin-1", errors="ignore")
            if mojibake_path != raw_path:
                candidates.append(LEGACY_MIRROR_ROOT / mojibake_path / "index.html")
                candidates.append(LEGACY_MIRROR_ROOT / mojibake_path)
        else:
            candidates.append(LEGACY_MIRROR_ROOT / "index.html")

        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return candidate

        self.stdout.write(self.style.WARNING(f"Legacy source not found for URL: {legacy_url}"))
        return None

    def _decode_legacy_html(self, raw_bytes):
        if not raw_bytes:
            return ""

        # Some mirrored pages are gzip-compressed despite the .html extension.
        if raw_bytes.startswith(b"\x1f\x8b"):
            try:
                raw_bytes = gzip.decompress(raw_bytes)
            except OSError:
                pass

        for encoding in ("utf-8", "cp1252", "latin-1"):
            try:
                text = raw_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
            if "<html" in text.lower() or "<!doctype" in text.lower():
                return text

        text = raw_bytes.decode("utf-8", errors="ignore")
        if "<html" in text.lower() or "<!doctype" in text.lower():
            return text
        return ""

    def _select_main_content_node(self, soup):
        selectors = [
            "#content_area",
            ".j-blog-single-entry",
            ".j-blog-article",
            ".j-blog-post",
            ".j-blog-content",
            "article",
            "#main",
        ]
        for selector in selectors:
            node = soup.select_one(selector)
            if node:
                return node
        return None

    def _normalize_legacy_image_src(self, src):
        raw_src = str(src or "").strip()
        if not raw_src or raw_src.startswith("data:"):
            return ""

        parsed = urlparse(raw_src)
        if parsed.scheme in {"http", "https"}:
            normalized = f"{parsed.netloc}{parsed.path}".lstrip("/")
        else:
            normalized = unquote(raw_src).replace("\\", "/")
            while normalized.startswith("../"):
                normalized = normalized[3:]
            normalized = normalized.lstrip("/")

        if not normalized:
            return ""

        transformed = (
            normalized.replace(":format=", "_format=")
            .replace(":rotate=", "_rotate=")
            .replace(":mode=", "_mode=")
        )

        variants = [
            transformed,
            normalized,
        ]

        unique_variants = []
        for variant in variants:
            if variant not in unique_variants:
                unique_variants.append(variant)

        for variant in unique_variants:
            imported_path = f"imported/{variant}"[:255]
            if self._image_file_exists(imported_path):
                return imported_path

        return f"imported/{unique_variants[0]}"[:255]

    def _pick_best_legacy_image_path(self, content_node):
        candidates = []
        for img in content_node.find_all("img"):
            src = img.get("src", "")
            imported_path = self._normalize_legacy_image_src(src)
            if not imported_path:
                continue

            if not self._image_file_exists(imported_path):
                self._maybe_download_legacy_image(src, imported_path)

            score = 0
            lower_path = imported_path.lower()
            if self._image_file_exists(imported_path):
                score += 100
            if "/image/" in lower_path:
                score += 20
            if "/logo/" in lower_path:
                score -= 20
            if "emotion/crop/header" in lower_path:
                score -= 40

            candidates.append((score, imported_path))

        if not candidates:
            return ""

        candidates.sort(key=lambda item: item[0], reverse=True)
        return candidates[0][1]

    def _image_file_exists(self, imported_path):
        rel = str(imported_path or "").replace("\\", "/").lstrip("/")
        if rel.startswith("imported/"):
            rel = rel[len("imported/") :]

        if not rel:
            return False

        media_candidate = PROJECT_ROOT / "media" / "imported" / rel
        mirror_candidate = PROJECT_ROOT / "scripts" / "ambre" / rel
        return media_candidate.exists() or mirror_candidate.exists()

    def _rewrite_legacy_asset_urls(self, content_html):
        if not content_html:
            return content_html

        soup = BeautifulSoup(content_html, "html.parser")

        for node in soup.find_all(True):
            for attr in ("src", "data-src", "href", "data-href"):
                original = node.get(attr)
                local = self._legacy_asset_to_media_url(original)
                if local:
                    node[attr] = local
                    continue

                if attr in {"href", "data-href"}:
                    internal = self._rewrite_legacy_internal_url(original)
                    if internal:
                        node[attr] = internal

            for attr in ("srcset", "data-srcset"):
                original_set = node.get(attr)
                local_set = self._rewrite_srcset(original_set)
                if local_set:
                    node[attr] = local_set

        return str(soup)

    def _normalize_imported_html(self, content_html):
        cleaned_html = self._clean_legacy_content_html(content_html)
        return self._rewrite_legacy_asset_urls(cleaned_html)

    def _clean_legacy_content_html(self, content_html):
        if not content_html:
            return content_html

        soup = BeautifulSoup(content_html, "html.parser")

        for node in soup.find_all(True):
            if "class" in node.attrs:
                del node.attrs["class"]
            if "id" in node.attrs:
                del node.attrs["id"]

            style_map = self._parse_style_declarations(node.get("style", ""))

            for prop in (
                "line-height",
                "font-family",
                "caret-color",
            ):
                style_map.pop(prop, None)

            # Legacy white-on-dark inline styles should not force default text color.
            color = style_map.get("color", "").strip().lower().replace(" ", "")
            if color in {"#fff", "#ffffff", "#000000"}:
                style_map.pop("color", None)
                style_map.pop("font-size", None)

            # Remove inline font-size and convert larger chunks to headings instead.
            font_size_value = style_map.pop("font-size", "")
            level = self._font_size_to_heading_level(font_size_value)
            if level and node.name in {"span", "p", "div"}:
                text_preview = node.get_text(" ", strip=True)
                if len(text_preview) >= 8:
                    node.name = level

            self._apply_style_map(node, style_map)

        for paragraph in list(soup.find_all("p")):
            if self._is_visually_empty_node(paragraph):
                paragraph.replace_with(soup.new_tag("br"))

        for span in list(soup.find_all("span")):
            if self._is_visually_empty_node(span):
                span.decompose()
                continue
            if not span.attrs:
                span.unwrap()

        for tag in list(soup.find_all(["p", "div"])):
            if self._is_visually_empty_node(tag):
                tag.replace_with(soup.new_tag("br"))

        for tag in list(soup.find_all(["h3", "h4"])):
            if self._is_visually_empty_node(tag):
                tag.decompose()

        self._collapse_adjacent_line_breaks(soup)

        return str(soup)

    def _collapse_adjacent_line_breaks(self, soup):
        previous_was_break = False
        for node in list(soup.descendants):
            if not getattr(node, "name", None):
                continue
            if node.name == "br":
                if previous_was_break:
                    node.decompose()
                    continue
                previous_was_break = True
            elif node.name not in {"span"}:
                previous_was_break = False

    def _parse_style_declarations(self, style_text):
        style_map = {}
        for chunk in str(style_text or "").split(";"):
            if ":" not in chunk:
                continue
            key, value = chunk.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            if key and value:
                style_map[key] = value
        return style_map

    def _apply_style_map(self, node, style_map):
        if not style_map:
            if "style" in node.attrs:
                del node.attrs["style"]
            return

        style_chunks = [f"{key}: {value}" for key, value in style_map.items()]
        node["style"] = "; ".join(style_chunks)

    def _font_size_to_heading_level(self, font_size_value):
        raw = str(font_size_value or "").strip().lower()
        if not raw:
            return ""

        match = re.search(r"(\d+(?:\.\d+)?)\s*(px|pt)?", raw)
        if not match:
            return ""

        value = float(match.group(1))
        unit = match.group(2) or "px"
        size_px = value * 1.333 if unit == "pt" else value

        if size_px >= 20:
            return "h3"
        if size_px >= 16:
            return "h4"
        return ""

    def _is_visually_empty_node(self, node):
        if node.find(["img", "video", "iframe", "object", "embed", "svg"]):
            return False

        text = node.get_text("", strip=False).replace("\xa0", " ")
        text = re.sub(r"\s+", "", text)
        return text == ""

    def _rewrite_srcset(self, srcset_value):
        raw = str(srcset_value or "").strip()
        if not raw:
            return ""

        rewritten_parts = []
        changed = False
        for part in [item.strip() for item in raw.split(",") if item.strip()]:
            bits = part.split()
            if not bits:
                continue
            local_url = self._legacy_asset_to_media_url(bits[0])
            if local_url:
                bits[0] = local_url
                changed = True
            rewritten_parts.append(" ".join(bits))

        if not rewritten_parts:
            return ""
        return ", ".join(rewritten_parts) if changed else raw

    def _legacy_asset_to_media_url(self, url_value):
        raw = str(url_value or "").strip()
        if not raw or raw.startswith("data:"):
            return ""

        if not self._is_legacy_image_url(raw):
            return ""

        imported_path = self._normalize_legacy_image_src(raw)
        if not imported_path:
            return ""

        if not self._image_file_exists(imported_path):
            self._maybe_download_legacy_image(raw, imported_path)

        if not self._image_file_exists(imported_path):
            return ""

        media_url = str(getattr(settings, "MEDIA_URL", "/media/") or "/media/")
        if not media_url.endswith("/"):
            media_url += "/"
        return f"{media_url}{imported_path.lstrip('/')}"

    def _is_legacy_image_url(self, raw_url):
        lower = raw_url.lower()
        if "image.jimcdn.com/" in lower:
            return True
        if lower.startswith("../image.jimcdn.com/") or lower.startswith("../../image.jimcdn.com/"):
            return True

        parsed = urlparse(raw_url)
        return parsed.netloc.lower() == "image.jimcdn.com"

    def _rewrite_legacy_internal_url(self, url_value):
        raw = str(url_value or "").strip()
        if not raw or raw.startswith("#") or raw.startswith("mailto:") or raw.startswith("tel:"):
            return ""

        parsed = urlparse(raw)
        if parsed.scheme in {"http", "https"}:
            host = parsed.netloc.lower()
            if "lessecretsdambre.com" not in host:
                return ""
            path = parsed.path
        elif parsed.scheme:
            return ""
        else:
            path = raw.split("#", 1)[0].split("?", 1)[0]

        normalized = unquote(path).replace("\\", "/")
        while normalized.startswith("../"):
            normalized = normalized[3:]
        normalized = normalized.lstrip("/")

        if normalized.endswith("/index.html"):
            normalized = normalized[: -len("/index.html")]
        elif normalized.endswith(".html"):
            normalized = normalized[: -len(".html")]
        normalized = normalized.strip("/")

        if not normalized:
            return "/"

        if normalized == "blog-beaute-et-bien-etre":
            return "/blog/"

        blog_lookup = {
            urlparse(item.get("legacy_url", "")).path.strip("/"): item.get("slug", "")
            for item in BLOG_POST_DEFINITIONS
            if item.get("legacy_url") and item.get("slug")
        }
        if normalized in blog_lookup and blog_lookup[normalized]:
            return f"/blog/{blog_lookup[normalized]}/"

        segments = normalized.split("/")
        top_level = segments[0]

        if top_level == "achat" and len(segments) > 1:
            service_slug = LEGACY_ACHAT_TO_SERVICE.get(segments[1])
            if service_slug:
                service_url = self._service_url(service_slug)
                if service_url:
                    return service_url

        service_slug = LEGACY_TOPLEVEL_TO_SERVICE.get(top_level)
        if service_slug:
            service_url = self._service_url(service_slug)
            if service_url:
                return service_url

        category_slug = LEGACY_TOPLEVEL_TO_CATEGORY.get(top_level)
        if category_slug:
            return f"/categorie/{category_slug}/"

        standalone_slug = LEGACY_STANDALONE_SLUG_MAP.get(top_level)
        if standalone_slug:
            return f"/page/{standalone_slug}/"

        return ""

    def _service_url(self, service_slug):
        for service_def in SERVICE_DEFINITIONS:
            if service_def.get("slug") == service_slug and service_def.get("category"):
                return f"/categorie/{service_def['category']}/soin/{service_slug}/"
        return ""

    def _compact_summary(self, summary_text, html_content, max_len=280):
        raw = re.sub(r"\s+", " ", str(summary_text or "")).strip()
        body_preview = self._extract_text_preview(html_content or "")

        if not raw:
            raw = body_preview
        if len(raw) > max_len * 2:
            raw = body_preview

        compact = re.sub(r"\s+", " ", str(raw or "")).strip()
        if len(compact) <= max_len:
            return compact

        cut = compact[:max_len].rstrip()
        for sep in (". ", "! ", "? ", "; ", ": "):
            idx = cut.rfind(sep)
            if idx >= int(max_len * 0.55):
                return cut[: idx + 1].strip()

        return cut.rstrip(" ,;:-") + "..."

    def _maybe_download_legacy_image(self, src, imported_path):
        parsed = urlparse(str(src or "").strip())
        if parsed.scheme not in {"http", "https"}:
            return

        rel = str(imported_path or "").replace("\\", "/").lstrip("/")
        if rel.startswith("imported/"):
            rel = rel[len("imported/") :]
        if not rel:
            return

        destination = PROJECT_ROOT / "media" / "imported" / rel
        if destination.exists():
            return

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            req = Request(str(src), headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=8) as response:
                data = response.read()
            if data:
                destination.write_bytes(data)
        except Exception:
            return

    def _extract_meta_content(self, soup, selector_specs):
        for tag_name, attrs in selector_specs:
            node = soup.find(tag_name, attrs=attrs)
            if not node:
                continue
            value = str(node.get("content", "")).strip()
            if value:
                return value
        return ""

    def _extract_text_preview(self, html_or_text):
        plain_text = BeautifulSoup(str(html_or_text), "html.parser").get_text(" ", strip=True)
        plain_text = re.sub(r"\s+", " ", plain_text).strip()
        return plain_text[:500]
