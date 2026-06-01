# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This repository is a resume/professional profile builder. The source of truth for the resume content is `docs/profile.md`. The `output/` directory is the designated location for any generated artifacts (PDF, HTML, JSON, etc.).

## Project Structure

- `docs/profile.md` — Professional profile and resume source content (Markdown)
- `docs/JD/sample_jd.md` — Example job description file for testing JD tailoring
- `output/` — Target directory for generated resume files
- `templates/` — Contains template reference PDFs and their paired generators
  - `ats-friendly.pdf` — Template reference for the ATS-friendly two-column layout
  - `ats_friendly_1col_generator.py` — Single-column ATS-safe PDF generator
  - `ats_friendly_2col_generator.py` — Two-column visual PDF generator
  - `ats_friendly_docx_generator.py` — DOCX generator
- `generate.py` — Entry point for all resume generation
- `tools/` — Helper modules for JD processing and AI tailoring
  - `jd_loader.py` — Loads a job description from a URL or local `.md`/`.txt` file
  - `jd_tailor.py` — Tailors resume content to a JD via Claude API (parallel sub-agents)

## How to Generate a Resume

Run from the project root using the Anaconda Python interpreter:

```bash
/opt/anaconda3/bin/python3 generate.py                              # base profile, both layouts
/opt/anaconda3/bin/python3 generate.py --layout 1col               # single-column ATS-safe PDF + DOCX
/opt/anaconda3/bin/python3 generate.py --layout 2col               # two-column visual PDF + DOCX
```

### JD-Tailored Generation

Provide a job description via `--jd` to generate a resume tailored to a specific role. Content is rewritten by Claude  using parallel sub-agents — one per resume section — to mirror the JD's language and priorities, using only facts from `docs/profile.md`.

```bash
/opt/anaconda3/bin/python3 generate.py --jd https://linkedin.com/jobs/view/...
/opt/anaconda3/bin/python3 generate.py --jd docs/JD/my_jd.md
/opt/anaconda3/bin/python3 generate.py --jd docs/JD/my_jd.md --layout 1col
```

Tailored output files are named with the company and role slug:
```
output/TJ_Tamilmani_Jayaraman_Resume_<Company>_<role_slug>_1col.pdf
output/TJ_Tamilmani_Jayaraman_Resume_<Company>_<role_slug>.pdf
output/TJ_Tamilmani_Jayaraman_Resume_<Company>_<role_slug>.docx
```
## RULES:
** DO NOT MODIFY profile.md. 

### Layouts

| Flag | Output file(s) | Best for |
|---|---|---|
| `--layout 1col` | `*_1col.pdf` + `.docx` | Automated ATS portal submissions |
| `--layout 2col` | `*.pdf` + `.docx` | Human reviewers, direct/email submissions |
| `--layout both` | All of the above | Default — generates everything |

### JD Input Options

| Input | Example |
|---|---|
| LinkedIn URL | `--jd https://www.linkedin.com/jobs/view/4393516363/` |
| Any public job posting URL | `--jd https://company.com/careers/vp-engineering` |
| Local Markdown file | `--jd docs/JD/my_jd.md` |
| Local text file | `--jd docs/JD/my_jd.txt` |

## JD Tailoring — How It Works

1. `tools/jd_loader.py` fetches and cleans the JD text (URL scraping or file read)
2. `tools/jd_tailor.py` sends `docs/profile.md` + JD to **Claude Sonnet (`claude-sonnet-4-6`) via Anthropic API** — 7 parallel sub-agents, one per resume section
3. Claude returns a structured JSON content dict — reordered, rephrased, keyword-matched to the JD
4. All three generators accept this content dict; base profile is used when no JD is provided

**Strict rule enforced in the prompt:** Claude may only use facts from `docs/profile.md` — no invented content.

## Adding a New Template

1. Add the template reference PDF to `templates/`
2. Create paired generators:
   - `templates/<name>_1col_generator.py` — single-column PDF; must expose `build(content=None)`
   - `templates/<name>_2col_generator.py` — two-column PDF; must expose `build(content=None)`
   - `templates/<name>_docx_generator.py` — DOCX; must expose `build(content=None)`
3. Register all three under the new template key in `TEMPLATES` dict in `generate.py`

## Profile Content

The profile in `docs/profile.md` belongs to **Tamilmani Jayaraman (TJ)**, a technology leader with 20+ years of experience in cloud infrastructure, DevSecOps, platform engineering, and AI/ML. When generating or formatting resume content, preserve the factual accuracy of roles, dates, and accomplishments exactly as written in the source document.

## Output
- Generate PDF and DOCX files and save them in the `output/` folder
- Use templates for structure and format
- Resumes must be ATS-friendly

## Review
- Review generated resumes for ATS compliance
- Provide an ATS score and summarize feedback and improvements in a `.md` file — one per format
- if JD provided, compare against JD and score on how close or fit the resume is with JD
- File name: `<output_filename>_review.md`
- Save review files in the `output/` folder
- Base profile reviews: `TJ__Resume_review.md` (2col) and `TJ__Resume_1col_review.md` (1col)
- JD-tailored reviews: `<tailored_output_filename>_review.md`
