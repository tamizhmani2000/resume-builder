#!/usr/bin/env python3
"""Entry point for resume generation.

Usage:
    python generate.py                                        # base profile, both layouts
    python generate.py --layout 1col                          # single-column PDF + DOCX
    python generate.py --layout 2col                          # two-column PDF + DOCX
    python generate.py --jd <url|path/to/jd.md>              # JD-tailored, both layouts
    python generate.py --jd <url|path/to/jd.md> --layout 1col

Layouts:
    1col  — Single-column, ATS-safe PDF (+ DOCX). Best for automated portal submissions.
    2col  — Two-column visual PDF (+ DOCX). Best for human/email review.
    both  — Generates both layouts (default).

When --jd is provided the resume content is tailored to the job description via
Claude. Output files are named with the company and role slug:
    TJ__Profile_<Company>_<role_slug>_1col.pdf
    TJ_Profile_<Company>_<role_slug>.pdf
    TJ_Profile_<Company>_<role_slug>.docx
"""

import argparse
import importlib.util
import os
import sys

# Add tools/ to path so jd_loader and jd_tailor are importable
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))

PROFILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "profile.md")

TEMPLATES = {
    "ats-friendly": {
        "1col": (
            "templates/ats_friendly_1col_generator.py",
            "templates/ats_friendly_docx_generator.py",
        ),
        "2col": (
            "templates/ats_friendly_2col_generator.py",
            "templates/ats_friendly_docx_generator.py",
        ),
    },
}
DEFAULT_TEMPLATE = "ats-friendly"
DEFAULT_LAYOUT   = "both"


def load_module(rel_path):
    abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_path)
    if not os.path.exists(abs_path):
        print(f"Generator not found: {abs_path}")
        sys.exit(1)
    spec = importlib.util.spec_from_file_location("generator", abs_path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(template_name, layout, jd_source=None):
    template = TEMPLATES.get(template_name)
    if not template:
        print(f"Unknown template '{template_name}'. Available: {', '.join(TEMPLATES)}")
        sys.exit(1)

    import reviewer
    import job_tracker

    # Optionally tailor content to JD
    content = None
    jd_text = None
    if jd_source:
        import jd_loader
        import jd_tailor
        print(f"\nLoading job description from: {jd_source}")
        jd_text = jd_loader.load(jd_source)
        content = jd_tailor.tailor(PROFILE_PATH, jd_text)

    layouts_to_run = list(template.keys()) if layout == "both" else [layout]
    docx_done = False
    docx_path = None
    pdf_paths = {}  # lyt -> path

    for lyt in layouts_to_run:
        if lyt not in template:
            print(f"Unknown layout '{lyt}'. Available: {', '.join(template)}")
            sys.exit(1)
        pdf_gen_path, docx_gen_path = template[lyt]
        print(f"\n── Generating {template_name} / {lyt} ──")

        pdf_mod = load_module(pdf_gen_path)
        pdf_result = pdf_mod.build(content)
        if isinstance(pdf_result, str):
            pdf_paths[lyt] = pdf_result

        if not docx_done:
            docx_mod = load_module(docx_gen_path)
            docx_path = docx_mod.build(content)
            docx_done = True

    # One review per run, based on the DOCX (PDFs are layout renders of the same content)
    review_path = None
    if docx_path:
        try:
            review_path = reviewer.review(content, jd_text, docx_path, layouts_to_run)
        except Exception as exc:
            print(f"  [warn] Review generation failed: {exc}")

    # Log to job application tracker (JD-tailored runs only)
    if jd_source and content and content.get("meta"):
        meta = content["meta"]
        try:
            job_tracker.log_application(
                company=meta.get("company", ""),
                role=meta.get("role", ""),
                jd_source=jd_source,
                layouts=layouts_to_run,
                pdf_1col=pdf_paths.get("1col", ""),
                pdf_2col=pdf_paths.get("2col", ""),
                docx=docx_path or "",
                review_path=review_path or "",
            )
        except Exception as exc:
            print(f"  [warn] Job tracker update failed: {exc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate TJ's resume PDF + DOCX.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python generate.py                             # both layouts, base profile\n"
            "  python generate.py --layout 1col              # single-column PDF + DOCX\n"
            "  python generate.py --layout 2col              # two-column PDF + DOCX\n"
            "  python generate.py --jd https://...           # tailored to JD from URL\n"
            "  python generate.py --jd jobs/acme_vp.md       # tailored to JD from file\n"
            "  python generate.py --jd jobs/acme_vp.md --layout 1col\n"
        ),
    )
    parser.add_argument(
        "--template", default=DEFAULT_TEMPLATE,
        help=f"Template name (default: {DEFAULT_TEMPLATE}). Choices: {', '.join(TEMPLATES)}"
    )
    parser.add_argument(
        "--layout", default=DEFAULT_LAYOUT, choices=["1col", "2col", "both"],
        help="Layout: 1col (ATS), 2col (visual), both (default)"
    )
    parser.add_argument(
        "--jd", default=None, metavar="URL_OR_PATH",
        help="Job description: a URL or path to a .md/.txt file. Triggers AI tailoring."
    )
    args = parser.parse_args()
    run(args.template, args.layout, jd_source=args.jd)
