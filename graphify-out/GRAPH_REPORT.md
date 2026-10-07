# Graph Report - resume-builder  (2026-10-07)

## Corpus Check
- Corpus is ~20,107 words - fits in a single context window. You may not need a graph.

## Summary
- 120 nodes · 223 edges · 8 communities (7 shown, 1 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.86)
- Token cost: 9,800 input · 2,400 output

## Community Hubs (Navigation)
- JD Tailoring & Claude API
- Pipeline Orchestration
- ReportLab PDF Engine
- DOCX Generator
- Two-Column Visual PDF
- Profile & Project Docs
- Cover Letter Generator
- Job Application Tracker

## God Nodes (most connected - your core abstractions)
1. `Tamilmani Jayaraman (TJ) Professional Profile — Resume Source of Truth` - 10 edges
2. `build()` - 9 edges
3. `build()` - 7 edges
4. `set_font()` - 7 edges
5. `_keyword_audit()` - 7 edges
6. `Resume Builder Project Guide (CLAUDE.md)` - 7 edges
7. `build_story()` - 6 edges
8. `call()` - 6 edges
9. `_load_url()` - 6 edges
10. `build_left()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `Resume Builder Project Guide (CLAUDE.md)` --references--> `ATS-Friendly Two-Column PDF Template Reference`  [EXTRACTED]
  CLAUDE.md → src/templates/ats-friendly.pdf
- `ATS Compliance Design Principle for Resume Output` --rationale_for--> `ATS-Friendly Two-Column PDF Template Reference`  [EXTRACTED]
  CLAUDE.md → src/templates/ats-friendly.pdf
- `Generate Resume Slash Command` --references--> `Tamilmani Jayaraman (TJ) Professional Profile — Resume Source of Truth`  [EXTRACTED]
  .claude/commands/generate_resume.md → docs/profile.md
- `Generate Resume Slash Command` --conceptually_related_to--> `JD Tailoring via 7 Parallel Claude Sub-agents`  [INFERRED]
  .claude/commands/generate_resume.md → CLAUDE.md
- `JD Tailoring via 7 Parallel Claude Sub-agents` --references--> `Tamilmani Jayaraman (TJ) Professional Profile — Resume Source of Truth`  [INFERRED]
  CLAUDE.md → docs/profile.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Candidate Job Description Pool for TJ Resume Tailoring** — docs_jd_adt_role, docs_jd_hd_role, docs_jd_remote_role, docs_jd_sample_jd_role, docs_jd_signet_role [INFERRED 0.95]
- **JD-Tailored Resume Generation Pipeline** — docs_profile_md_profile, jd_tailoring_parallel_agents, src_templates_ats_friendly_template, docs_workflow_index_pipeline [EXTRACTED 0.95]
- **Resume Quality and Compliance Constraints** — profile_immutability_rule, ats_compliance_principle, docs_profile_md_profile [INFERRED 0.85]

## Communities (8 total, 1 thin omitted)

### Community 0 - "JD Tailoring & Claude API"
Cohesion: 0.15
Nodes (9): call(), _apply_corrections(), _call_parallel(), _call_section(), _extract_profile_sections(), _keyword_audit(), _parse_json(), tailor() (+1 more)

### Community 1 - "Pipeline Orchestration"
Cohesion: 0.17
Nodes (8): load_module(), run(), _clean(), _extract_linkedin_jd(), _fetch_url(), load(), _load_file(), _load_url()

### Community 2 - "ReportLab PDF Engine"
Cohesion: 0.16
Nodes (7): b(), build(), build_story(), _from_content(), _html_escape(), _output_path(), sec()

### Community 3 - "DOCX Generator"
Cohesion: 0.24
Nodes (9): build(), bullet(), edu_entry(), job_entry(), _output_path(), para(), _resolve(), section_header() (+1 more)

### Community 4 - "Two-Column Visual PDF"
Cohesion: 0.25
Nodes (10): b(), build(), build_header(), build_left(), build_right(), frame(), _html_escape(), _output_path() (+2 more)

### Community 5 - "Profile & Project Docs"
Cohesion: 0.27
Nodes (11): Generate Resume Slash Command, Resume Builder Project Guide (CLAUDE.md), ADT Senior Director Machine Learning and AI Job Description, Home Depot Software Engineer Manager AI/ML Platforms Job Description, Remote VP Engineering Vertical SaaS Role Job Description, Sample VP Engineering Cloud Platform Job Description (Acme Corp), Signet IT Director Store Solutions Engineering and Architecture Job Description, Tamilmani Jayaraman (TJ) Professional Profile — Resume Source of Truth (+3 more)

### Community 6 - "Cover Letter Generator"
Cohesion: 0.42
Nodes (6): _build_docx(), _generate_content(), main(), _para(), _parse_json(), _set_font()

## Knowledge Gaps
- **1 isolated node(s):** `Signet IT Director Store Solutions Engineering and Architecture Job Description`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 31 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_parse_scores()` connect `Job Application Tracker` to `Pipeline Orchestration`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `Tamilmani Jayaraman (TJ) Professional Profile — Resume Source of Truth` (e.g. with `ADT Senior Director Machine Learning and AI Job Description` and `Home Depot Software Engineer Manager AI/ML Platforms Job Description`) actually correct?**
  _`Tamilmani Jayaraman (TJ) Professional Profile — Resume Source of Truth` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Signet IT Director Store Solutions Engineering and Architecture Job Description` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `JD Tailoring & Claude API` be split into smaller, more focused modules?**
  _Cohesion score 0.14624505928853754 - nodes in this community are weakly interconnected._