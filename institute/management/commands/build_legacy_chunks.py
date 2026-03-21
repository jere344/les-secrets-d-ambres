import json
import re
from pathlib import Path

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand


DEFAULT_INPUT = Path(__file__).parent / "seed_maps" / "legacy_content.json"
DEFAULT_OUTPUT = Path(__file__).parent / "seed_maps" / "legacy_chunks.json"


class Command(BaseCommand):
    help = "Build a chunk catalog from legacy_content.json for manual content placement."

    def add_arguments(self, parser):
        parser.add_argument(
            "--input",
            default=str(DEFAULT_INPUT),
            help="Input legacy content JSON path",
        )
        parser.add_argument(
            "--output",
            default=str(DEFAULT_OUTPUT),
            help="Output legacy chunks JSON path",
        )
        parser.add_argument(
            "--min-text-length",
            type=int,
            default=80,
            help="Minimum text length to keep a module chunk",
        )

    def handle(self, *args, **options):
        input_path = Path(options["input"]).resolve()
        output_path = Path(options["output"]).resolve()
        min_text_length = int(options["min_text_length"])

        if not input_path.exists():
            self.stdout.write(self.style.ERROR(f"Input file not found: {input_path}"))
            return

        payload = json.loads(input_path.read_text(encoding="utf-8"))
        source_pages = payload.get("source_pages", {})

        out_sources = {}
        chunk_index = {}
        total_chunks = 0

        for source_ref, source_payload in source_pages.items():
            html = source_payload.get("html") or ""
            chunks = self._extract_chunks(source_ref, html, min_text_length)
            out_sources[source_ref] = {
                "title": source_payload.get("title", ""),
                "summary": source_payload.get("summary", ""),
                "legacy_url": source_payload.get("legacy_url", ""),
                "chunks": chunks,
            }
            for chunk in chunks:
                chunk_index[chunk["id"]] = {
                    "source_ref": source_ref,
                    "title": chunk["title"],
                    "html": chunk["html"],
                    "text_preview": chunk["text_preview"],
                }
            total_chunks += len(chunks)

        result = {
            "generated_from": str(input_path),
            "source_count": len(out_sources),
            "chunk_count": total_chunks,
            "source_pages": out_sources,
            "chunk_index": chunk_index,
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, ensure_ascii=True, indent=2), encoding="utf-8")

        self.stdout.write(
            self.style.SUCCESS(
                f"Legacy chunk catalog written to {output_path} "
                f"({len(out_sources)} sources, {total_chunks} chunks)."
            )
        )

    def _extract_chunks(self, source_ref: str, html: str, min_text_length: int):
        soup = BeautifulSoup(html, "html.parser")
        container = soup.select_one("#content_area") or soup

        for tag in container.select("script, style, noscript"):
            tag.decompose()

        chunks = []
        module_nodes = container.select("div.j-module")
        if module_nodes:
            for node in module_nodes:
                chunk = self._to_chunk_dict(source_ref, node, min_text_length, len(chunks) + 1)
                if chunk:
                    chunks.append(chunk)

        if not chunks:
            fallback_chunk = self._to_chunk_dict(source_ref, container, min_text_length, 1)
            if fallback_chunk:
                chunks.append(fallback_chunk)

        return chunks

    def _to_chunk_dict(self, source_ref: str, node, min_text_length: int, position: int):
        fragment = BeautifulSoup(str(node), "html.parser")
        for tag in fragment.select("script, style, noscript"):
            tag.decompose()

        text = " ".join(fragment.stripped_strings)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) < min_text_length:
            return None

        heading = fragment.find(["h1", "h2", "h3"])
        title = heading.get_text(" ", strip=True) if heading else text[:80]

        chunk_id = f"{source_ref}::{position:03d}"
        return {
            "id": chunk_id,
            "title": title[:180],
            "text_preview": text[:220],
            "html": str(fragment),
        }
