#!/usr/bin/env python3
"""Load a job description from a URL or a local .md/.txt file.

Returns clean plain text suitable for passing to jd_tailor.py.
"""

import os
import re
import sys


def _fetch_url(url: str) -> str:
    """Fetch URL content using curl (respects system/corporate CA certs) or requests."""
    import subprocess
    ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE")
    cmd = [
        "curl", "-sL", "--max-time", "30",
        "-A", (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
    ]
    if ca_bundle:
        cmd += ["--cacert", ca_bundle]
    cmd.append(url)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
    if result.returncode != 0:
        sys.exit(f"Failed to fetch URL: {result.stderr.strip()}")
    return result.stdout


def _load_url(url: str) -> str:
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        sys.exit("Missing dependencies: pip install beautifulsoup4")

    html = _fetch_url(url)
    soup = BeautifulSoup(html, "html.parser")

    # Remove boilerplate elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # LinkedIn-specific: extract only the job details section to avoid noise
    if "linkedin.com" in url:
        text = _extract_linkedin_jd(soup)
        if text:
            return _clean(text)

    text = soup.get_text(separator="\n")
    return _clean(text)


def _extract_linkedin_jd(soup) -> str:
    """Extract only the actual job description text from a LinkedIn job page."""
    # Try known LinkedIn job-description containers
    selectors = [
        {"class": re.compile(r"description__text", re.I)},
        {"class": re.compile(r"jobs-description", re.I)},
        {"class": re.compile(r"job-details", re.I)},
    ]
    for attrs in selectors:
        node = soup.find(attrs=attrs)
        if node:
            return node.get_text(separator="\n")

    # Fallback: grab everything up to "Similar jobs" or "People also viewed"
    full_text = soup.get_text(separator="\n")
    cutoff = re.search(
        r"\n(Similar jobs|People also viewed|Show more jobs|Explore top content)",
        full_text,
        re.I,
    )
    if cutoff:
        full_text = full_text[: cutoff.start()]

    # Also trim anything before "About the Role" or "Job Description"
    start = re.search(r"\n(About the Role|Job Description|About This Role)", full_text, re.I)
    if start:
        full_text = full_text[start.start():]

    return full_text


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
