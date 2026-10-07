#!/usr/bin/env python3
"""Generate ATS compliance and JD-fit review markdown for a generated resume.

Called once per generate.py run, based on the DOCX (the authoritative source document).
PDFs are layout renders of the same content, so only one review is needed per run.
Output: <docx_stem>_review.md in the same output/ directory.
"""

import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import claude_client

_SYSTEM_PROMPT = """\
You are an expert ATS compliance reviewer and technical recruiting specialist with deep \
knowledge of how Applicant Tracking Systems parse resumes and how hiring managers evaluate \
candidate fit. You produce accurate, specific, and actionable resume reviews.
"""

_PROMPT_TEMPLATE = """\
Review the resume content below and write a complete ATS compliance and JD fit review in Markdown.

## Metadata
- Candidate: Tamilmani Jayaraman (TJ)
- Source document: {docx_filename}
- Generated layouts: {layouts_desc}
- Review date: {today}
{role_line}

## Resume Content (JSON — this is what was written into the DOCX and PDFs)
{content_json}

## Job Description
{jd_section}

---

## Instructions: Write the Review in Markdown

Start directly with the `#` heading. Output pure Markdown only — no code fences around the \
whole document, no preamble, no commentary outside the review itself.

Structure the review with these sections in order:

### Section 1 — Header block
```
# Resume Review — <Company>: <Role Title>
**Candidate:** Tamilmani Jayaraman (TJ)
**Target Role:** <role> — <company>
**Source Document:** `{docx_filename}`
**Generated Layouts:** {layouts_desc}
**Review Date:** {today}
```

### Section 2 — ATS Compliance Score: XX / 100

The DOCX is the master document; PDFs are layout renders. Score the DOCX content for \
ATS compliance — not the visual layout. DOCX format is natively well-parsed by all major \
ATS systems (Workday, Taleo, Greenhouse, iCIMS), so layout-related deductions do not apply here.

Write "## ATS Compliance Score: XX / 100" as a heading, then include a Markdown table with \
columns: Check | Status (✅ Pass / ⚠️ Risk / ❌ Fail) | Notes.

Check these items:
- Standard section headers (Summary, Experience, Skills, Education, Certifications)
- Reverse-chronological work history
- Consistent date format throughout
- Contact info present in body
- No embedded graphics or images that trap text
- ATS keyword coverage — check each major JD keyword individually as a separate row
- Keyword recency — are critical skills evidenced in recent roles (last 3-5 years)?

After the table, list Deductions as bullet points with point values, e.g. \
"(-5) Apache Airflow absent — explicit JD hard-filter keyword". Briefly explain each.

Baseline: start from 100. Typical deductions: -3 to -5 per missing hard-filter keyword, \
-2 for minor issues (date inconsistency, recency gaps, implied-but-not-named skills).

### Section 3 — JD Fit Score: XX / 100
(If no JD was provided, write "## Profile Coverage" and assess completeness vs profile instead.)

Include:
- 1-2 sentence role alignment summary
- Strengths table: JD Requirement | TJ Evidence | Strength (★ to ★★★★★)
- Gaps table: JD Requirement | Gap | Severity (High/Medium/Low) | Recommendation

### Section 4 — Overall Assessment
2-3 focused paragraphs. Be direct and specific. \
End with a numbered list of the top 3 actionable improvements for before submission.

### Section 5 — Submission Guide
Short table: Submission Channel | Which File to Use.
Cover: ATS portal, recruiter email, LinkedIn Easy Apply, direct to hiring manager, DOCX required.

### Section 6 — Keyword Coverage vs JD
Markdown table: JD Keyword | Present in Resume? (✅ / ⚠️ Implied / ❌ Missing)
Include 20-25 key terms extracted from the JD. If no JD was provided, skip this section.
"""


def review(
    content: dict | None,
    jd_text: str | None,
    docx_path: str,
    layouts: list[str],
) -> str:
    """Build and save an ATS + JD-fit review .md file based on the DOCX.

    Called once per generate.py run. Returns the path to the saved review file.
    """
    docx_filename = os.path.basename(docx_path)
    review_path = os.path.splitext(docx_path)[0] + "_review.md"

    layouts_desc = " + ".join(
        "1col PDF (ATS portal)" if l == "1col" else "2col PDF (visual/human)" for l in layouts
    )

    role_line = ""
    if content and content.get("meta"):
        meta = content["meta"]
        role_line = f"- Target Role: {meta.get('role', '')} — {meta.get('company', '')}"

    # Compact JSON (no indentation) keeps the same data at ~40% fewer characters
    content_json = json.dumps(content, separators=(",", ":")) if content else "(base profile — no JD tailoring applied)"
    # Cap JD at 4000 chars — the reviewer only needs the requirements, not full boilerplate
    if jd_text:
        jd_raw = jd_text.strip()
        jd_section = jd_raw[:4000] + ("\n...[truncated]" if len(jd_raw) > 4000 else "")
    else:
        jd_section = "(No JD provided — ATS compliance review only)"

    prompt = _PROMPT_TEMPLATE.format(
        docx_filename=docx_filename,
        layouts_desc=layouts_desc,
        today=date.today().isoformat(),
        role_line=role_line,
        content_json=content_json,
        jd_section=jd_section,
    )

    print(f"  Generating review...")
    md_text = claude_client.call(_SYSTEM_PROMPT, prompt).strip()

    with open(review_path, "w", encoding="utf-8") as f:
        f.write(md_text)

    print(f"Review saved: {review_path}")
    return review_path
