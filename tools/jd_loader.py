#!/usr/bin/env python3
"""Load a job description from a URL or a local .md/.txt file.

Returns clean plain text suitable for passing to jd_tailor.py.
"""

import os
import re
import sys


def _load_url(url: str) -> str:
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        sys.exit("Missing dependencies: pip install requests beautifulsoup4")

    headers = {"User-Agent": "Mozilla/5.0 (compatible; resume-builder/1.0)"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove navigation, scripts, styles, footers
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    return _clean(text)


def _load_file(path: str) -> str:
    if not os.path.exists(path):
        sys.exit(f"JD file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return _clean(f.read())


def _clean(text: str) -> str:
    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespace per line
    lines = [line.strip() for line in text.splitlines()]
    # Drop lines that are purely whitespace or very short noise
    lines = [l for l in lines if len(l) > 1 or l == ""]
    return "\n".join(lines).strip()


def load(source: str) -> str:
    """Load JD from a URL or file path. Returns clean text."""
    if source.startswith("http://") or source.startswith("https://"):
        return _load_url(source)
    return _load_file(source)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python jd_loader.py <url|path>")
        sys.exit(1)
    print(load(sys.argv[1]))
