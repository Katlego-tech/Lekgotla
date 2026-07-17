"""Lekgotla local API: compile AI configs into a scoped AGENTS.md manifest."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).parent.resolve()
PORT = 4173


@dataclass(frozen=True)
class RulePattern:
    key: str
    title: str
    section: str
    pattern: re.Pattern[str]
    value: Callable[[re.Match[str]], str]
    render: Callable[[str], str]


RULE_PATTERNS = (
    RulePattern(
        "packageManager",
        "Package manager",
        "Project rules",
        re.compile(r"\b(?:use|install(?: packages)? with)\s+(pnpm|npm|yarn|bun)\b", re.I),
        lambda match: match[1].lower(),
        lambda value: f"Use {value} for all package operations.",
    ),
    RulePattern(
        "testCommand",
        "Test command",
        "Project rules",
        re.compile(r"\b((?:pnpm|npm|yarn|bun)\s+test)\b", re.I),
        lambda match: match[1].lower(),
        lambda value: f"Run {value} before handoff.",
    ),
    RulePattern(
        "typescript",
        "TypeScript",
        "Project rules",
        re.compile(r"\b(prefer typescript|avoid\s+any)\b", re.I),
        lambda match: "strict",
        lambda value: "Prefer TypeScript; avoid any.",
    ),
    RulePattern(
        "commitStyle",
        "Commit style",
        "Delivery",
        re.compile(r"\b(conventional commits?|descriptive commit messages?)\b", re.I),
        lambda match: "conventional" if "conventional" in match[1].lower() else "descriptive",
        lambda value: (
            "Follow conventional commits." if value == "conventional" else "Write descriptive commit messages."
        ),
    ),
    RulePattern(
        "secrets",
        "Secrets policy",
        "Delivery",
        re.compile(r"\b(never commit secrets|do not commit secrets|never commit.*env)\b", re.I),
        lambda match: "protect",
        lambda value: "Never commit secrets or local env files.",
    ),
)


def estimate_tokens(text: str) -> int:
    """A transparent local token estimate; replace with a model tokenizer in production."""
    return max(1, round(len(re.findall(r"\S+", text.strip())) * 1.28))


def compile_manifest(sources: list[dict[str, str]], resolutions: dict[str, str] | None = None) -> dict[str, Any]:
    resolutions = resolutions or {}
    candidates: dict[str, list[dict[str, Any]]] = {}
    passthrough: list[str] = []
    for source in sources:
        for raw_line in source.get("content", "").splitlines():
            line = re.sub(r"^\s*[-*]\s*", "", raw_line).strip()
            if not line:
                continue
            pattern = next((item for item in RULE_PATTERNS if item.pattern.search(line)), None)
            if not pattern:
                if len(line) > 10:
                    passthrough.append(line)
                continue
            match = pattern.pattern.search(line)
            assert match
            rule = {
                "key": pattern.key,
                "title": pattern.title,
                "section": pattern.section,
                "value": pattern.value(match),
                "render": pattern.render,
                "text": line,
                "source": source["name"],
            }
            candidates.setdefault(pattern.key, []).append(rule)

    conflicts, selected = [], []
    for key, rules in candidates.items():
        unique = list({rule["value"]: rule for rule in rules}.values())
        selected.append(next((rule for rule in rules if rule["value"] == resolutions.get(key)), rules[0]))
        if len(unique) > 1:
            conflicts.append(
                {
                    "key": key,
                    "title": selected[-1]["title"],
                    "options": [
                        {"value": rule["value"], "text": rule["text"], "source": rule["source"]} for rule in unique
                    ],
                    "severity": "high" if key == "packageManager" else "medium",
                }
            )

    sections: dict[str, list[str]] = {}
    for rule in selected:
        sections.setdefault(rule["section"], []).append(rule["render"](rule["value"]))
    if passthrough:
        sections["Additional guidance"] = list(dict.fromkeys(passthrough[:3]))
    sections["Context routing"] = ["frontend → src/components, src/app", "backend → src/api, db, tests"]
    manifest_lines = ["# Lekgotla Manifest", ""]
    for heading, rules in sections.items():
        manifest_lines += [f"## {heading}", *(f"- {rule}" for rule in rules), ""]
    manifest = "\n".join(manifest_lines).rstrip() + "\n"
    input_tokens = sum(estimate_tokens(source.get("content", "")) for source in sources)
    output_tokens = estimate_tokens(manifest)
    return {
        "manifest": manifest,
        "conflicts": conflicts,
        "directives": len(selected) + len(passthrough),
        "inputTokens": input_tokens,
        "outputTokens": output_tokens,
        "reclaimed": max(0, round((1 - output_tokens / input_tokens) * 100)) if input_tokens else 0,
    }


def context_bundle(manifest: str, task: str) -> dict[str, Any]:
    routes = {
        "ui": ("Build checkout UI", ("project rules", "context routing"), "components · design system · test rules"),
        "api": (
            "Fix orders API timeout",
            ("project rules", "delivery", "context routing"),
            "API contracts · database · test rules",
        ),
        "review": ("Review payment PR", ("delivery", "project rules"), "commit rules · security · test rules"),
    }
    name, words, areas = routes.get(task, routes["ui"])
    blocks = manifest.split("## ")
    bundle = (
        "".join(
            block for block in blocks if block.startswith("# Lekgotla") or any(word in block.lower() for word in words)
        ).strip()
        + "\n"
    )
    tokens, full_tokens = estimate_tokens(bundle), estimate_tokens(manifest)
    return {
        "task": name,
        "bundle": bundle,
        "tokens": tokens,
        "rules": len(re.findall(r"^-", bundle, re.M)),
        "areas": areas,
        "reduction": max(0, round((1 - tokens / full_tokens) * 100)),
    }


class LekgotlaHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/health":
            return self.send_json(HTTPStatus.OK, {"status": "ok"})
        return super().do_GET()

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 1_000_000:
                return self.send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "Request body exceeds 1 MB"})
            body = json.loads(self.rfile.read(length) or "{}")
            if self.path == "/api/compile":
                sources = body.get("sources")
                invalid_sources = not isinstance(sources, list) or any(
                    not isinstance(item, dict)
                    or not isinstance(item.get("name"), str)
                    or not isinstance(item.get("content"), str)
                    for item in sources
                )
                if invalid_sources:
                    return self.send_json(
                        HTTPStatus.BAD_REQUEST,
                        {"error": "sources must be an array of { name, content }"},
                    )
                return self.send_json(HTTPStatus.OK, compile_manifest(sources, body.get("resolutions")))
            if self.path == "/api/context":
                if not isinstance(body.get("manifest"), str):
                    return self.send_json(HTTPStatus.BAD_REQUEST, {"error": "manifest must be a string"})
                return self.send_json(HTTPStatus.OK, context_bundle(body["manifest"], body.get("task", "ui")))
            return self.send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
        except (json.JSONDecodeError, ValueError):
            return self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON body"})
        except Exception as error:  # pragma: no cover - final API safety net
            return self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(error)})

    def send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), LekgotlaHandler)
    print(f"Lekgotla running at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
