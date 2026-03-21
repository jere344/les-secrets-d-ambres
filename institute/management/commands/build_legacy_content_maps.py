import json
from pathlib import Path

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from .seed_maps import CATEGORY_DEFINITIONS, SERVICE_DEFINITIONS


class Command(BaseCommand):
    help = "Build legacy source content dictionary JSON from HTTrack mirror."

    def add_arguments(self, parser):
        parser.add_argument(
            "--mirror-dir",
            default="scripts/ambre",
            help="Path to HTTrack mirror root (default: scripts/ambre)",
        )
        parser.add_argument(
            "--output",
            default="institute/management/commands/seed_maps/legacy_content.json",
            help="Output JSON path for extracted source content",
        )

    def handle(self, *args, **options):
        mirror_root = Path(options["mirror_dir"]).resolve()
        legacy_site_root = mirror_root / "www.lessecretsdambre.com"
        output_path = Path(options["output"]).resolve()

        if not legacy_site_root.exists():
            self.stdout.write(self.style.ERROR(f"Mirror not found: {legacy_site_root}"))
            return

        source_refs = []
        for item in CATEGORY_DEFINITIONS:
            source_refs.extend(item.get("sources", []))
        for item in SERVICE_DEFINITIONS:
            source_refs.extend(item.get("sources", []))

        ordered_unique_sources = list(dict.fromkeys(source_refs))
        indexed_top_pages = self._index_legacy_top_pages(legacy_site_root)

        source_pages = {}
        missing = []

        for source_ref in ordered_unique_sources:
            page_file = self._resolve_source_ref_to_page(legacy_site_root, indexed_top_pages, source_ref)
            if not page_file:
                missing.append(source_ref)
                continue

            parsed = self._parse_legacy_page(page_file)
            source_pages[source_ref] = {
                "title": parsed["title"],
                "summary": parsed["summary"],
                "html": parsed["html"],
                "legacy_url": f"https://www.lessecretsdambre.com/{source_ref.strip('/')}/",
            }

        payload = {
            "generated_from": legacy_site_root.as_posix(),
            "source_count": len(source_pages),
            "missing_sources": missing,
            "source_pages": source_pages,
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

        self.stdout.write(
            self.style.SUCCESS(
                f"Legacy content map written to {output_path} "
                f"({len(source_pages)} sources, {len(missing)} missing)."
            )
        )

    def _index_legacy_top_pages(self, legacy_site_root: Path):
        indexed = {}
        for child in legacy_site_root.iterdir():
            if not child.is_dir():
                continue
            index_file = child / "index.html"
            if not index_file.exists():
                continue
            normalized = slugify(child.name)
            if normalized:
                indexed[normalized] = index_file
        return indexed

    def _resolve_source_ref_to_page(self, legacy_site_root: Path, indexed_top_pages, source_ref: str):
        clean_ref = source_ref.strip("/")
        direct = legacy_site_root / clean_ref / "index.html"
        if direct.exists():
            return direct

        if clean_ref.startswith("achat/"):
            achat_slug = slugify(clean_ref.split("/", 1)[1])
            achat_dir = legacy_site_root / "achat"
            if achat_dir.exists():
                for child in achat_dir.iterdir():
                    index_file = child / "index.html"
                    if child.is_dir() and index_file.exists() and slugify(child.name) == achat_slug:
                        return index_file

        if "/" not in clean_ref:
            return indexed_top_pages.get(slugify(clean_ref))

        return None

    def _parse_legacy_page(self, page_file: Path):
        html = page_file.read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(html, "html.parser")

        content = soup.select_one("#content_area") or soup.select_one("#content") or soup.body or soup
        fragment = BeautifulSoup(str(content), "html.parser")

        for tag in fragment.select("script, style, noscript"):
            tag.decompose()

        for img in fragment.find_all("img"):
            img.attrs.pop("srcset", None)
            img.attrs.pop("sizes", None)

        title_node = fragment.find("h1") or fragment.find("h2")
        title = title_node.get_text(" ", strip=True) if title_node else ""
        if not title and soup.title:
            title = soup.title.get_text(" ", strip=True).split(" - ")[0].strip()

        summary = ""
        for p in fragment.find_all("p"):
            text = p.get_text(" ", strip=True)
            if len(text) >= 40:
                summary = text
                break

        return {"title": title[:180], "summary": summary[:1200], "html": str(fragment)}
