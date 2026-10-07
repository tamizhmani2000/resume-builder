# Job Application Tracker

> 7 nodes

## Key Concepts

- **job_tracker.py** (7 connections) — `src/tools/job_tracker.py`
- **log_application()** (4 connections) — `src/tools/job_tracker.py`
- **_parse_scores()** (4 connections) — `src/tools/job_tracker.py`
- **csv** (2 connections)
- **Track job applications — one row per resume generation run. Appends to…** (1 connections) — `src/tools/job_tracker.py`
- **Extract ATS and JD Fit scores from a review markdown file.** (1 connections) — `src/tools/job_tracker.py`
- **Append one application row to docs/job_applications.csv.** (1 connections) — `src/tools/job_tracker.py`

## Relationships

- [Pipeline Orchestration](Pipeline_Orchestration.md) (2 shared connections)
- [Cover Letter Generator](Cover_Letter_Generator.md) (1 shared connections)
- [JD Tailoring & Claude API](JD_Tailoring_&_Claude_API.md) (1 shared connections)

## Source Files

- `src/tools/job_tracker.py`

## Audit Trail

- EXTRACTED: 12 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*