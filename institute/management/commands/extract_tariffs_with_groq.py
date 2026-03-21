import json
import os
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from .seed_maps import SERVICE_CONTENT_ASSIGNMENTS, SERVICE_CONTENT_OVERRIDES, SERVICE_DEFINITIONS

LEGACY_CHUNKS_JSON_PATH = Path(__file__).parent / "seed_maps" / "legacy_chunks.json"
OUTPUT_JSON_PATH = Path(__file__).parent / "seed_maps" / "tariff_ai_extracted.json"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile"


class Command(BaseCommand):
    help = "Extract tariff rows from raw legacy HTML using Groq and save structured JSON."

    def add_arguments(self, parser):
        parser.add_argument("--model", default=DEFAULT_MODEL, help="Groq model name")
        parser.add_argument("--service", action="append", default=[], help="Service slug to process (repeatable)")
        parser.add_argument("--max-requests", type=int, default=0, help="Limit number of service requests")
        parser.add_argument("--timeout", type=int, default=90, help="HTTP timeout in seconds")
        parser.add_argument("--overwrite", action="store_true", help="Overwrite output file (default: merge)")

    def handle(self, *args, **options):
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            self.stderr.write(self.style.ERROR("Missing GROQ_API_KEY environment variable."))
            return

        catalog = self._load_chunk_catalog()
        if not catalog:
            self.stderr.write(self.style.ERROR("Missing or invalid legacy chunk catalog."))
            return

        selected_slugs = set(options["service"] or [])
        max_requests = int(options["max_requests"] or 0)
        timeout = int(options["timeout"] or 90)
        model = options["model"]

        existing = {} if options.get("overwrite") else self._load_existing_output()
        output = dict(existing)

        processed = 0
        attempted = 0
        for service_def in SERVICE_DEFINITIONS:
            slug = service_def.get("slug", "")
            if not slug:
                continue
            if selected_slugs and slug not in selected_slugs:
                continue
            if max_requests and attempted >= max_requests:
                break
            attempted += 1

            raw_html = self._get_service_raw_html(slug, catalog)
            if not raw_html.strip():
                self.stdout.write(self.style.WARNING(f"[{slug}] skipped: empty raw html"))
                continue

            reduced_html = self._reduce_html_for_ai(raw_html)

            try:
                rows = self._extract_with_groq(
                    api_key=api_key,
                    model=model,
                    service_slug=slug,
                    service_title=service_def.get("title", slug),
                    raw_html=reduced_html,
                    timeout=timeout,
                )
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f"[{slug}] failed: {exc}"))
                continue

            output[slug] = rows
            processed += 1
            self.stdout.write(f"[{slug}] extracted {len(rows)} rows")

        OUTPUT_JSON_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Saved {len(output)} service entries to {OUTPUT_JSON_PATH}"))

    def _load_chunk_catalog(self):
        if not LEGACY_CHUNKS_JSON_PATH.exists():
            return {}
        try:
            payload = json.loads(LEGACY_CHUNKS_JSON_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except Exception:
            return {}
        return {}

    def _load_existing_output(self):
        if not OUTPUT_JSON_PATH.exists():
            return {}
        try:
            payload = json.loads(OUTPUT_JSON_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except Exception:
            return {}
        return {}

    def _get_service_raw_html(self, slug, catalog):
        assignment = SERVICE_CONTENT_ASSIGNMENTS.get(slug, {})
        override = SERVICE_CONTENT_OVERRIDES.get(slug, {})

        source_pages = catalog.get("source_pages", {})
        chunk_index = catalog.get("chunk_index", {})

        html_parts = []
        override_html = str(override.get("details_html", "") or "").strip()
        if override_html:
            html_parts.append(override_html)

        seen = set()

        for chunk_id in assignment.get("chunk_ids", []):
            payload = chunk_index.get(chunk_id)
            if not payload:
                continue
            chunk_html = str(payload.get("html", "") or "").strip()
            if chunk_html:
                html_parts.append(chunk_html)
            seen.add(chunk_id)

        for source_ref in assignment.get("source_refs", []):
            source_payload = source_pages.get(source_ref) or {}
            for chunk in source_payload.get("chunks", []):
                chunk_id = chunk.get("id")
                if chunk_id and chunk_id in seen:
                    continue
                chunk_html = str(chunk.get("html", "") or "").strip()
                if chunk_html:
                    html_parts.append(chunk_html)

        return "\n".join(html_parts)

    def _extract_with_groq(self, api_key, model, service_slug, service_title, raw_html, timeout):
        prompt = self._build_prompt(service_slug, service_title, raw_html)
        body = {
            "model": model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You extract tariff rows from messy HTML. "
                        "Return only valid JSON object. "
                        "Never paraphrase text; preserve wording exactly from source."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        resp = None
        for attempt in range(4):
            resp = requests.post(GROQ_ENDPOINT, headers=headers, json=body, timeout=timeout)
            if resp.status_code != 429:
                break
            wait_seconds = 8 + (attempt * 4)
            time.sleep(wait_seconds)

        if resp is None:
            raise RuntimeError("No response from Groq API")
        if resp.status_code >= 300:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:500]}")

        payload = resp.json()
        content = (
            payload.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        json_text = self._extract_json_block(content)
        parsed = json.loads(json_text)

        rows = parsed.get("tariffs", []) if isinstance(parsed, dict) else []
        if not isinstance(rows, list):
            rows = []

        source_text = self._normalize_compare_text(BeautifulSoup(raw_html, "html.parser").get_text(" ", strip=True))

        normalized = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            label = str(row.get("label", "")).strip()
            price_label = str(row.get("price_label", "")).strip()
            if not label or not price_label:
                continue

            # Guardrails against hallucinated placeholders and paraphrases.
            if re.fullmatch(r"tarif\s*\d+", label.strip().lower()):
                continue
            if not self._is_fragment_in_source(label, source_text):
                continue
            if not self._is_fragment_in_source(price_label, source_text):
                continue

            notes = str(row.get("notes", "")).strip()
            if notes and not self._is_fragment_in_source(notes, source_text):
                notes = ""

            details_html = str(row.get("details_html", "")).strip()
            if details_html:
                details_text = BeautifulSoup(details_html, "html.parser").get_text(" ", strip=True)
                if details_text and not self._is_fragment_in_source(details_text, source_text):
                    details_html = ""

            normalized.append(
                {
                    "label": label,
                    "price_label": price_label,
                    "duration_text": str(row.get("duration_text", "")).strip(),
                    "notes": notes,
                    "details_html": details_html,
                }
            )

        return normalized

    def _reduce_html_for_ai(self, raw_html):
        raw = str(raw_html or "").strip()
        if not raw:
            return ""

        # Keep tariff-rich structures first to stay inside free-tier token limits.
        soup = BeautifulSoup(raw, "html.parser")
        parts = []

        for table in soup.find_all("table"):
            html = str(table).strip()
            if html:
                parts.append(html)

        for node in soup.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
            text = node.get_text(" ", strip=True)
            if not text:
                continue
            if re.search(r"\d", text) or any(mark in text.lower() for mark in ["eur", "€", "tarif", "prix", "min"]):
                parts.append(f"<{node.name}>{text}</{node.name}>")

        reduced = "\n".join(parts) if parts else raw

        # Compact whitespace so more table rows fit before truncation.
        reduced = re.sub(r">\s+<", "><", reduced)
        reduced = re.sub(r"\s+", " ", reduced).strip()

        max_chars = 20000
        if len(reduced) > max_chars:
            reduced = reduced[:max_chars]
        return reduced

    def _extract_json_block(self, text):
        stripped = text.strip()
        if stripped.startswith("{") and stripped.endswith("}"):
            return stripped

        fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", stripped, flags=re.S)
        if fenced:
            return fenced.group(1)

        first = stripped.find("{")
        last = stripped.rfind("}")
        if first >= 0 and last > first:
            return stripped[first : last + 1]

        raise ValueError("No JSON object found in model response")

    def _normalize_compare_text(self, value):
        text = str(value or "").replace("\xa0", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip().lower()

    def _is_fragment_in_source(self, fragment, source_text):
        probe = self._normalize_compare_text(fragment)
        if not probe:
            return False
        if probe in source_text:
            return True

        # Fallback for long text where tiny punctuation differences may occur.
        if len(probe) > 80:
            compact_probe = re.sub(r"[^a-z0-9àâäçéèêëîïôöùûüÿæœ€]+", "", probe)
            compact_source = re.sub(r"[^a-z0-9àâäçéèêëîïôöùûüÿæœ€]+", "", source_text)
            return bool(compact_probe) and compact_probe in compact_source

        return False

    def _build_prompt(self, service_slug, service_title, raw_html):
        # Keep prompt concise to reduce tokens while forcing strict schema.
        return (
            "Task: extract tariff rows from RAW HTML for one service.\n"
            "Service slug: " + service_slug + "\n"
            "Service title: " + service_title + "\n\n"
            "Output JSON schema (strict):\n"
            "{\n"
            '  "service_slug": "string",\n'
            '  "tariffs": [\n'
            "    {\n"
            '      "label": "string",\n'
            '      "price_label": "string",\n'
            '      "duration_text": "string",\n'
            '      "notes": "string",\n'
            '      "details_html": "string"\n'
            "    }\n"
            "  ]\n"
            "}\n\n"
            "Rules:\n"
            "1) VERBATIM ONLY: every string must be copied exactly from source. Never rewrite, simplify, translate, or correct grammar.\n"
            "2) If a value is not explicitly present in source, use an empty string for that field.\n"
            "3) Keep currency symbols, spacing, punctuation, apostrophes, and accents exactly as seen.\n"
            "4) Exclude non-tariff text and exclude generic placeholders (forbidden examples: 'Tarif 1', 'Tarif standard').\n"
            "5) When a tariff row is followed by descriptive lines/bullets before the next tariff row, copy that description verbatim into notes.\n"
            "6) notes must be plain text copied verbatim; details_html must contain only HTML fragments copied verbatim from source.\n"
            "7) Return only JSON object, no explanation.\n\n"
            "RAW HTML START\n"
            + raw_html
            + "\nRAW HTML END\n"
        )
