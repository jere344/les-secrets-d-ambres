import json
import re
from collections import defaultdict
from pathlib import Path

from django.core.management.base import BaseCommand
from PIL import Image, UnidentifiedImageError
from rapidocr_onnxruntime import RapidOCR


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".avif"}
TOKEN_PATTERN = re.compile(r"(i[0-9a-f]{8,32})", re.IGNORECASE)


class Command(BaseCommand):
    help = "Run OCR on mirrored legacy images and persist a reusable image catalog."

    def add_arguments(self, parser):
        parser.add_argument(
            "--mirror-dir",
            default="scripts/ambre",
            help="Path to the HTTrack mirror root (default: scripts/ambre)",
        )
        parser.add_argument(
            "--output",
            default="institute/management/commands/seed_maps/legacy_image_ocr_catalog.json",
            help="Output JSON file path for OCR catalog",
        )
        parser.add_argument(
            "--min-confidence",
            type=float,
            default=0.35,
            help="Minimum average OCR confidence to classify image as text-bearing",
        )

    def handle(self, *args, **options):
        mirror_root = Path(options["mirror_dir"]).resolve()
        output_path = Path(options["output"]).resolve()
        min_confidence = float(options["min_confidence"])

        if not mirror_root.exists():
            self.stdout.write(self.style.ERROR(f"Mirror directory not found: {mirror_root}"))
            return

        image_files = sorted(
            [
                path
                for path in mirror_root.rglob("*")
                if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
            ]
        )
        html_files = sorted([path for path in mirror_root.rglob("*.html") if path.is_file()])

        if not image_files:
            self.stdout.write(self.style.WARNING(f"No image files found under {mirror_root}"))
            return

        self.stdout.write(
            f"Cataloging {len(image_files)} images and indexing {len(html_files)} HTML files..."
        )

        image_tokens = defaultdict(list)
        for image_path in image_files:
            rel = image_path.relative_to(mirror_root).as_posix()
            token = self._extract_token(rel)
            if token:
                image_tokens[token].append(rel)

        token_to_pages = self._build_token_page_map(html_files, image_tokens, mirror_root)

        engine = RapidOCR()
        catalog_rows = []
        text_images = 0
        illustration_images = 0
        page_illustration_candidates = defaultdict(list)
        page_text_candidates = defaultdict(list)

        for idx, image_path in enumerate(image_files, start=1):
            rel = image_path.relative_to(mirror_root).as_posix()
            token = self._extract_token(rel)
            usage_pages = sorted(token_to_pages.get(token, [])) if token else []

            width, height = self._read_dimensions(image_path)
            ocr_lines, avg_confidence = self._run_ocr(engine, image_path)
            joined_text = " ".join([line["text"] for line in ocr_lines]).strip()
            word_count = len([w for w in re.split(r"\s+", joined_text) if w]) if joined_text else 0

            has_text = bool(ocr_lines) and avg_confidence >= min_confidence
            if has_text:
                text_images += 1
                classification = "text"
            else:
                illustration_images += 1
                classification = "illustration"

            catalog_rows.append(
                {
                    "relative_path": rel,
                    "token": token,
                    "classification": classification,
                    "ocr_text": joined_text,
                    "ocr_line_count": len(ocr_lines),
                    "ocr_average_confidence": round(avg_confidence, 4),
                    "ocr_lines": ocr_lines,
                    "word_count": word_count,
                    "char_count": len(joined_text),
                    "width": width,
                    "height": height,
                    "size_bytes": image_path.stat().st_size,
                    "usage_count": len(usage_pages),
                    "usage_pages": usage_pages,
                }
            )

            candidate_entry = {
                "relative_path": rel,
                "token": token,
                "width": width,
                "height": height,
                "size_bytes": image_path.stat().st_size,
                "ocr_line_count": len(ocr_lines),
                "ocr_average_confidence": round(avg_confidence, 4),
                "ocr_text_preview": joined_text[:220],
            }
            for page in usage_pages:
                if classification == "illustration":
                    page_illustration_candidates[page].append(candidate_entry)
                else:
                    page_text_candidates[page].append(candidate_entry)

            if idx % 25 == 0 or idx == len(image_files):
                self.stdout.write(f"Processed {idx}/{len(image_files)} images")

        catalog = {
            "mirror_root": mirror_root.as_posix(),
            "language_hint": "fr",
            "ocr_engine": "rapidocr-onnxruntime",
            "thresholds": {
                "min_confidence": min_confidence,
            },
            "summary": {
                "total_images": len(image_files),
                "text_images": text_images,
                "illustration_images": illustration_images,
                "html_files_indexed": len(html_files),
            },
            "page_index": {
                "illustration_candidates": self._rank_page_candidates(page_illustration_candidates),
                "text_candidates": self._rank_page_candidates(page_text_candidates),
            },
            "images": catalog_rows,
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=True), encoding="utf-8")

        self.stdout.write(
            self.style.SUCCESS(
                f"OCR catalog written to {output_path} "
                f"({text_images} text images, {illustration_images} illustrations)."
            )
        )

    def _extract_token(self, text):
        match = TOKEN_PATTERN.search(text)
        return match.group(1).lower() if match else None

    def _build_token_page_map(self, html_files, image_tokens, mirror_root):
        token_to_pages = defaultdict(set)
        tracked_tokens = set(image_tokens.keys())

        for html_path in html_files:
            content = html_path.read_text(encoding="utf-8", errors="ignore")
            found_tokens = {token.lower() for token in TOKEN_PATTERN.findall(content)}
            found_tokens &= tracked_tokens
            if not found_tokens:
                continue

            rel_page = html_path.relative_to(mirror_root).as_posix()
            for token in found_tokens:
                token_to_pages[token].add(rel_page)

        return {token: sorted(pages) for token, pages in token_to_pages.items()}

    def _read_dimensions(self, image_path):
        try:
            with Image.open(image_path) as img:
                return img.width, img.height
        except (UnidentifiedImageError, OSError):
            return None, None

    def _run_ocr(self, engine, image_path):
        try:
            result, _ = engine(str(image_path))
        except Exception:
            return [], 0.0

        if not result:
            return [], 0.0

        rows = []
        confidences = []
        for item in result:
            if len(item) < 3:
                continue
            text = str(item[1]).strip()
            if not text:
                continue
            try:
                confidence = float(item[2])
            except (TypeError, ValueError):
                confidence = 0.0

            rows.append(
                {
                    "text": text,
                    "confidence": round(confidence, 4),
                }
            )
            confidences.append(confidence)

        if not rows:
            return [], 0.0

        avg_confidence = sum(confidences) / len(confidences)
        return rows, avg_confidence

    def _rank_page_candidates(self, page_candidate_map):
        ranked = {}
        for page, candidates in page_candidate_map.items():
            deduped = {}
            for candidate in candidates:
                key = candidate["relative_path"]
                deduped[key] = candidate

            sorted_candidates = sorted(
                deduped.values(),
                key=lambda item: ((item.get("width") or 0) * (item.get("height") or 0), item.get("size_bytes") or 0),
                reverse=True,
            )
            ranked[page] = sorted_candidates[:12]
        return ranked