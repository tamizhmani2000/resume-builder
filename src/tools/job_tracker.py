#!/usr/bin/env python3
"""Track job applications — one row per resume generation run.

Appends to docs/job_applications.csv. Called automatically by generate.py
after a JD-tailored resume is generated and reviewed.

Columns:
    date_applied, company, role, jd_source, layouts,
    ats_score, jd_fit_score, status,
    output_pdf_1col, output_pdf_2col, output_docx, review_file, notes
"""

import csv
import os
import re
from datetime import date

_HERE = os.path.dirname(os.path.abspath(__file__))
TRACKER_PATH = os.path.join(_HERE, "..", "docs", "job_applications.csv")

COLUMNS = [
    "date_applied",
    "company",
    "role",
    "jd_source",
    "layouts",
    "ats_score",
    "jd_fit_score",
    "status",
    "output_pdf_1col",
    "output_pdf_2col",
    "output_docx",
    "review_file",
    "notes",
]


def _parse_scores(review_path: str) -> tuple[str, str]:
    """Extract ATS and JD Fit scores from a review markdown file."""
    ats_score = ""
    jd_score = ""
    if not review_path or not os.path.exists(review_path):
        return ats_score, jd_score
    with open(review_path, encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"ATS Compliance Score:\s*(\d+)\s*/\s*100", text)
    if m:
        ats_score = m.group(1)
    m = re.search(r"JD Fit Score:\s*(\d+)\s*/\s*100", text)
    if m:
        jd_score = m.group(1)
    return ats_score, jd_score


def log_application(
    *,
    company: str,
    role: str,
    jd_source: str,
    layouts: list[str],
    pdf_1col: str = "",
    pdf_2col: str = "",
    docx: str = "",
    review_path: str = "",
    notes: str = "",
    status: str = "Applied",
) -> None:
    """Append one application row to docs/job_applications.csv."""
    ats_score, jd_fit_score = _parse_scores(review_path)

    row = {
        "date_applied":   date.today().isoformat(),
        "company":        company,
        "role":           role,
        "jd_source":      jd_source,
        "layouts":        "+".join(layouts),
        "ats_score":      ats_score,
        "jd_fit_score":   jd_fit_score,
        "status":         status,
        "output_pdf_1col": os.path.basename(pdf_1col) if pdf_1col else "",
        "output_pdf_2col": os.path.basename(pdf_2col) if pdf_2col else "",
        "output_docx":    os.path.basename(docx) if docx else "",
        "review_file":    os.path.basename(review_path) if review_path else "",
        "notes":          notes,
    }

    file_exists = os.path.exists(TRACKER_PATH)
    with open(TRACKER_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"  Application logged: {company} — {role} ({date.today().isoformat()})")
