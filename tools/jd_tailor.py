#!/usr/bin/env python3
"""Tailor resume content to a job description using Claude API directly.

Uses parallel sub-agents — each responsible for one resume section — so that
every section gets a focused prompt rather than one monolithic call.

Input:  profile text (docs/profile.md) + JD text
Output: dict with keys matching the content structure expected by generators

The model is instructed to only use facts from the profile — no invented content.
"""

import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import anthropic

MODEL_ID = "claude-sonnet-4-6"

SYSTEM_PROMPT = """\
You are an expert resume writer. Your task is to tailor a technology executive's \
resume content to match a specific job description.

STRICT RULES:
1. Only use facts, roles, companies, dates, metrics, and skills that appear in the \
   provided profile. Do NOT invent, embellish, or add any information not present.
2. Reorder, rephrase, and emphasize content to match the language and priorities \
   of the job description.
3. Mirror keywords and phrases from the JD where they are accurate — ATS systems \
   score on exact keyword matches.
4. Keep all bullet points concise (one sentence each, under 20 words preferred).
5. Always expand acronyms on first use in summary and first job (e.g., \
   "Site Reliability Engineering (SRE)").
6. Return ONLY valid JSON — no markdown fences, no commentary outside the JSON.
7. NEVER mention the hiring company or organization from the JD anywhere in the \
   resume content (summary, highlights, experience, skills, or any other section). \
   The resume must be company-agnostic — it describes the candidate's background only.
"""

# ---------------------------------------------------------------------------
# Per-section prompts — each agent gets the full profile + JD but a narrowly
# scoped output schema so it can focus on quality for that section.
# ---------------------------------------------------------------------------

SECTION_PROMPTS = {
    "meta": """\
Extract job metadata from the JD. Return JSON:
{{"meta": {{"company": "<hiring company name>", "role": "<job title>", "role_slug": "<lowercase-hyphenated-title>"}}}}
""",

    "header": """\
Return the candidate's tagline and competencies, reordered to foreground JD-relevant skills.
Return JSON:
{{
  "tagline": "<pipe-separated areas of expertise — reorder to match JD priority>",
  "competencies": "<dot-separated list — reorder to foreground JD-relevant skills>"
}}
""",

    "summary": """\
Write a 3-bullet executive summary tailored to this JD. Use only facts from the profile.
Return JSON:
{{"summary": ["<bullet 1>", "<bullet 2>", "<bullet 3>"]}}
""",

    "highlights": """\
Reorder the 7 career highlights from the profile so the most JD-relevant ones come first. \
Keep all 7. Rephrase where needed to mirror JD language — only use facts from the profile.
Return JSON:
{{"highlights": [{{"title": "<achievement title>", "desc": "<one sentence>"}}]}}
""",

    "experience": """\
Rewrite each job's bullets to mirror JD language where accurate. Keep exact titles, \
companies, and dates from the profile. Include ALL roles.
If the JD is an Individual Contributor (IC) role — i.e. it emphasises hands-on coding, \
engineering delivery, or technical depth over people management — reorder bullets within \
each role to lead with hands-on technical contributions (architecture, coding, CI/CD, \
platform engineering) and place management/budget/vendor bullets at the end.
Return JSON:
{{"experience": [
  {{"title": "<exact title>", "company": "<exact company>", "dates": "<exact dates>",
    "bullets": ["<bullet>", ...]}}
]}}
""",

    "skills": """\
Return technical skills and certifications from the profile. \
Reorder skill categories to foreground JD-relevant ones first. \
CRITICAL: Do NOT omit any skill, framework, tool, or technology listed in the profile — \
include every item even if not directly JD-relevant. Preserve exact names (e.g. Angular, \
ReactJS must both appear if both are in the profile).
Return JSON:
{{
  "technical_skills": ["<bold label>: <skill list>", ...],
  "certifications": ["<cert 1>", ...]
}}
""",

    "education": """\
Return education exactly as in the profile.
Return JSON:
{{"education": [{{"degree": "<degree>", "institution": "<institution  ·  year>"}}]}}
""",
}

SECTION_CONTEXT = """\
## Candidate Profile
{profile}

## Job Description
{jd}

## Your Task
{task}
"""


def _parse_json(raw: str) -> dict:
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Extract the outermost {...} block in case of leading/trailing prose
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            return json.loads(m.group())
        raise


def _call_section(section: str, profile: str, jd: str) -> tuple[str, dict]:
    prompt = SECTION_CONTEXT.format(
        profile=profile,
        jd=jd,
        task=SECTION_PROMPTS[section],
    )

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment
    message = client.messages.create(
        model=MODEL_ID,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text
    return section, _parse_json(raw)


def _call_parallel(profile: str, jd: str) -> dict:

    results: dict = {}
    sections = list(SECTION_PROMPTS.keys())

    with ThreadPoolExecutor(max_workers=len(sections)) as pool:
        futures = {
            pool.submit(_call_section, section, profile, jd): section
            for section in sections
        }
        for future in as_completed(futures):
            section = futures[future]
            try:
                _, data = future.result()
                results[section] = data
                print(f"  [done] {section}")
            except Exception as exc:
                print(f"  [warn] {section} failed ({exc}), retrying...", file=sys.stderr)
                try:
                    _, data = _call_section(section, profile, jd)
                    results[section] = data
                    print(f"  [done] {section} (retry)")
                except Exception as exc2:
                    print(f"  [error] {section}: {exc2}", file=sys.stderr)
                    raise

    # Merge all section dicts into one flat content dict
    content = {}
    for section_data in results.values():
        content.update(section_data)

    return content


def tailor(profile_path: str, jd_text: str) -> dict:
    """Return tailored content dict for the given JD."""
    with open(profile_path, "r", encoding="utf-8") as f:
        profile = f.read()

    print("Calling Claude sub-agents in parallel to tailor content...")
    content = _call_parallel(profile, jd_text)
    print(f"Tailored for: {content['meta']['company']} — {content['meta']['role']}")
    return content


if __name__ == "__main__":
    import jd_loader
    if len(sys.argv) != 2:
        print("Usage: python jd_tailor.py <url|path/to/jd.md>")
        sys.exit(1)
    profile_path = os.path.join(os.path.dirname(__file__), "..", "docs", "profile.md")
    jd_text = jd_loader.load(sys.argv[1])
    result = tailor(profile_path, jd_text)
    print(json.dumps(result, indent=2))
