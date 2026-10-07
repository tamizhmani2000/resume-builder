# Pipeline Orchestration

> 20 nodes

## Key Concepts

- **jd_loader.py** (11 connections) — `src/tools/jd_loader.py`
- **re** (10 connections)
- **sys** (10 connections)
- **generate.py** (8 connections) — `src/generate.py`
- **_load_url()** (6 connections) — `src/tools/jd_loader.py`
- **_clean()** (4 connections) — `src/tools/jd_loader.py`
- **_extract_linkedin_jd()** (4 connections) — `src/tools/jd_loader.py`
- **_fetch_url()** (4 connections) — `src/tools/jd_loader.py`
- **load()** (4 connections) — `src/tools/jd_loader.py`
- **_load_file()** (4 connections) — `src/tools/jd_loader.py`
- **load_module()** (3 connections) — `src/generate.py`
- **run()** (3 connections) — `src/generate.py`
- **concurrent_futures** (2 connections)
- **Entry point for resume generation. Usage: python generate.py # base profile,…** (1 connections) — `src/generate.py`
- **Load JD from a URL or file path. Returns clean text.** (1 connections) — `src/tools/jd_loader.py`
- **Fetch URL content using curl (respects system/corporate CA certs) or requests.** (1 connections) — `src/tools/jd_loader.py`
- **Load a job description from a URL or a local .md/.txt file. Returns clean plain…** (1 connections) — `src/tools/jd_loader.py`
- **Extract only the actual job description text from a LinkedIn job page.** (1 connections) — `src/tools/jd_loader.py`
- **argparse** (1 connections)
- **importlib_util** (1 connections)

## Relationships

- [JD Tailoring & Claude API](JD_Tailoring_&_Claude_API.md) (7 shared connections)
- [Cover Letter Generator](Cover_Letter_Generator.md) (5 shared connections)
- [Job Application Tracker](Job_Application_Tracker.md) (2 shared connections)

## Source Files

- `src/generate.py`
- `src/tools/jd_loader.py`

## Audit Trail

- EXTRACTED: 47 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*