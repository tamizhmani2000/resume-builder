#!/usr/bin/env python3
"""Generate a tailored cover letter (.docx) for any job description.

Usage:
    python tools/cover_letter_generator.py --jd <url|path/to/jd.md>

Output is written to output/ using the same naming convention as the resume generators:
    TJ_Tamilmani_Jayaraman_CoverLetter_<Company>_<role_slug>.docx
"""

import json
import os
import re
import sys
from datetime import date

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

DARK = RGBColor(0x1A, 0x1A, 0x1A)
GRAY = RGBColor(0x6B, 0x6B, 0x6B)
GOLD = RGBColor(0xC4, 0x9A, 0x3C)

_HERE = os.path.dirname(os.path.abspath(__file__))
PROFILE_PATH = os.path.join(_HERE, "..", "..", "docs", "profile.md")
OUTPUT_DIR   = os.path.join(_HERE, "..", "..", "output")

CANDIDATE = "Tamilmani Jayaraman (TJ)"
CONTACT   = "Irving, TX  |  tamizhmani2000@gmail.com  |  (201) 290-9366  |  linkedin.com/in/tamizh"

SYSTEM_PROMPT = """\
You are an expert executive cover letter writer. Write a brief, compelling cover letter \
for a senior technology leader. Executives read fast — every sentence must earn its place.

STRICT RULES:
1. Only use facts, roles, companies, dates, metrics, and skills that appear in the \
   provided candidate profile. Do NOT invent or embellish anything.
2. Mirror the JD's vocabulary naturally — no keyword stuffing.
3. First person. Confident, direct tone. No filler: no "excited to apply", \
   no "results-driven leader", no throat-clearing.
4. Length: exactly 3 short paragraphs. Each paragraph is 3–4 sentences maximum. \
   The entire letter should fit on half a page. Brevity is a feature, not a constraint.
5. Return ONLY valid JSON — no markdown fences, no commentary. Format:
   {
     "company": "<hiring company name>",
     "role": "<exact job title>",
     "role_slug": "<lowercase-hyphenated-title>",
     "paragraphs": ["<paragraph 1>", "<paragraph 2>", "<paragraph 3>"]
   }
"""

COVER_LETTER_PROMPT = """\
## Candidate Profile
{profile}

## Job Description
{jd}

## Your Task
Write a brief, executive-level cover letter — 3 paragraphs, 3–4 sentences each. \
No paragraph should run longer than 4 sentences.

Paragraph structure:
1. Hook (3–4 sentences) — Open with the single most compelling reason the candidate \
   is already doing this job. Name the current role and one specific, quantified proof \
   point that mirrors the JD's hardest requirement. No preamble.
2. Proof (3–4 sentences) — Pick the 2–3 most relevant achievements from the profile \
   that speak directly to the JD's core responsibilities. Be concrete: name the \
   company, the outcome, the metric. Use the JD's exact vocabulary where it fits \
   naturally. Do NOT list everything — pick the sharpest evidence only.
3. Fit + CTA (3–4 sentences) — One sentence on what specifically draws the candidate \
   to this company's mission or platform challenge (genuine, not flattery). \
   One sentence connecting the candidate's arc to where this role goes. \
   Close with a clean, single-sentence call to action.

Return JSON as specified in the system prompt.
"""


def _parse_json(raw: str) -> dict:
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            return json.loads(m.group())
        raise


def _generate_content(profile: str, jd: str) -> dict:
    import claude_client
    prompt = COVER_LETTER_PROMPT.format(profile=profile, jd=jd)
    raw = claude_client.call(SYSTEM_PROMPT, prompt)
    return _parse_json(raw)


# ── DOCX helpers ──────────────────────────────────────────────────────────────

def _set_font(run, size, bold=False, color=None, italic=False):
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color


def _para(doc, text="", size=10.5, bold=False, color=None, italic=False,
          align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=6):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    if text:
        run = p.add_run(text)
        _set_font(run, size, bold=bold, color=color, italic=italic)
    return p


def _build_docx(content: dict, out_path: str):
    doc = Document()

    for section in doc.sections:
        section.top_margin    = Inches(0.85)
        section.bottom_margin = Inches(0.85)
        section.left_margin   = Inches(1.0)
        section.right_margin  = Inches(1.0)

    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(10.5)

    # Name
    name_p = doc.add_paragraph()
    name_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    name_p.paragraph_format.space_before = Pt(0)
    name_p.paragraph_format.space_after = Pt(2)
    _set_font(name_p.add_run(CANDIDATE), 18, bold=True, color=DARK)

    # Contact line
    contact_p = doc.add_paragraph()
    contact_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    contact_p.paragraph_format.space_before = Pt(0)
    contact_p.paragraph_format.space_after = Pt(10)
    _set_font(contact_p.add_run(CONTACT), 9, color=GRAY)

    # Gold rule
    hr = doc.add_paragraph()
    hr.paragraph_format.space_before = Pt(0)
    hr.paragraph_format.space_after = Pt(14)
    _set_font(hr.add_run("─" * 90), 8, color=GOLD)

    # Date
    _para(doc, date.today().strftime("%B %d, %Y"), size=10.5, space_after=14)

    # Addressee block
    _para(doc, f"Hiring Team — {content['role']}", size=10.5, bold=True, space_after=2)
    _para(doc, content["company"], size=10.5, space_after=14)

    # Salutation
    _para(doc, "Dear Hiring Manager,", size=10.5, space_after=14)

    # Body paragraphs
    for para_text in content["paragraphs"]:
        _para(doc, para_text, size=10.5, space_after=12)

    # Closing
    _para(doc, "Sincerely,", size=10.5, space_before=10, space_after=22)
    sig = doc.add_paragraph()
    sig.paragraph_format.space_before = Pt(0)
    sig.paragraph_format.space_after = Pt(2)
    _set_font(sig.add_run(CANDIDATE), 10.5, bold=True, color=DARK)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    doc.save(out_path)
    print(f"Cover letter saved: {out_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate a tailored cover letter (.docx)")
    parser.add_argument("--jd", required=True, help="JD URL or path to .md/.txt file")
    args = parser.parse_args()

    sys.path.insert(0, _HERE)
    import jd_loader

    print(f"Loading job description from: {args.jd}")
    jd_text = jd_loader.load(args.jd)

    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        profile = f.read()

    print("Generating cover letter via Claude...")
    content = _generate_content(profile, jd_text)

    company  = content.get("company", "Company")
    slug     = content.get("role_slug", "role")
    filename = (
        f"TJ_Tamilmani_Jayaraman_CoverLetter"
        f"_{company.replace(' ', '_')}"
        f"_{slug.replace('-', '_')}.docx"
    )
    out_path = os.path.join(OUTPUT_DIR, filename)

    print(f"Tailored for: {company} — {content.get('role', '')}")
    _build_docx(content, out_path)


if __name__ == "__main__":
    main()
