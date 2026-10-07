# JD Tailoring & Claude API

> 23 nodes

## Key Concepts

- **jd_tailor.py** (15 connections) — `src/tools/jd_tailor.py`
- **_keyword_audit()** (7 connections) — `src/tools/jd_tailor.py`
- **reviewer.py** (7 connections) — `src/tools/reviewer.py`
- **json** (7 connections)
- **call()** (6 connections) — `src/tools/claude_client.py`
- **_call_parallel()** (5 connections) — `src/tools/jd_tailor.py`
- **_parse_json()** (5 connections) — `src/tools/jd_tailor.py`
- **claude_client.py** (5 connections) — `src/tools/claude_client.py`
- **_call_section()** (4 connections) — `src/tools/jd_tailor.py`
- **_extract_profile_sections()** (4 connections) — `src/tools/jd_tailor.py`
- **review()** (4 connections) — `src/tools/reviewer.py`
- **tailor()** (3 connections) — `src/tools/jd_tailor.py`
- **datetime** (3 connections)
- **_apply_corrections()** (2 connections) — `src/tools/jd_tailor.py`
- **subprocess** (2 connections)
- **Shared Claude CLI caller for all tools.** (1 connections) — `src/tools/claude_client.py`
- **Single-turn Claude call via the CLI. Returns the text response.** (1 connections) — `src/tools/claude_client.py`
- **Tailor resume content to a job description using the claude CLI. Uses parallel…** (1 connections) — `src/tools/jd_tailor.py`
- **Post-tailoring keyword gap analysis and targeted correction pass.** (1 connections) — `src/tools/jd_tailor.py`
- **Split profile.md into named chunks keyed by normalised ## heading slug.** (1 connections) — `src/tools/jd_tailor.py`
- **Return tailored content dict for the given JD.** (1 connections) — `src/tools/jd_tailor.py`
- **Build and save an ATS + JD-fit review .md file based on the DOCX. Called once…** (1 connections) — `src/tools/reviewer.py`
- **Generate ATS compliance and JD-fit review markdown for a generated resume.…** (1 connections) — `src/tools/reviewer.py`

## Relationships

- [Pipeline Orchestration](Pipeline_Orchestration.md) (7 shared connections)
- [Cover Letter Generator](Cover_Letter_Generator.md) (5 shared connections)
- [Job Application Tracker](Job_Application_Tracker.md) (1 shared connections)

## Source Files

- `src/tools/claude_client.py`
- `src/tools/jd_tailor.py`
- `src/tools/reviewer.py`

## Audit Trail

- EXTRACTED: 49 (98%)
- INFERRED: 1 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*