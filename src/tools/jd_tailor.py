#!/usr/bin/env python3
"""Tailor resume content to a job description using the claude CLI.

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

import claude_client

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
8. Gap-analysis pass: before finalising your output, identify the 5–10 most critical \
   JD keywords for this section. For any that are absent from your draft, check whether \
   the profile contains analogous work that can be accurately reframed in the JD's \
   vocabulary. Surface those analogues — ONLY where factually accurate.
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
If the JD is in financial services, fintech, or auto finance:
- Explicitly reference any financial services domain exposure in the profile \
  (e.g. loan underwriting, account management, SOX-compliant environments, payment processing, \
  credit card platforms, regulated financial systems) to establish domain credibility.
- Use domain vocabulary that mirrors the JD: "customer account servicing," \
  "financial operations platforms," "regulated financial services," or equivalent — \
  only where the profile supports it.
If the JD is for a D2C, consumer health, telehealth, subscription commerce, or \
subscription-first company (signals: "subscription", "recurring", "subscriber", \
"telehealth", "clinical", "health platform", "D2C"):
- Surface any health-adjacent domain work from the profile (pharmacy eCommerce, \
  health data environments, regulated consumer data) to establish domain credibility.
- Reframe any recurring billing, auto-pay, or B2B payment scheduling work using \
  subscription vocabulary (e.g. "recurring billing", "subscription commerce") — \
  only where the underlying work justifies it.
- Use "conversion and retention" as paired commerce success metrics where the \
  profile supports both.
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
If the JD is in financial services, fintech, or auto finance:
- For each role, foreground any bullets that reference financial domain work: \
  loan underwriting, account management, payment processing, SOX compliance, \
  regulatory controls, PCI DSS, credit platforms, or financial operations systems.
- In older roles (e.g. Cognizant Principal Lead) where financial services work exists, \
  ensure those bullets appear first within that role's list to maximize domain signal.
If the JD is an AI/ML platform or data engineering role:
- Restate any machine learning model training, deployment, pipeline, or monitoring work \
  using explicit MLOps vocabulary: "MLOps", "model deployment", "model monitoring", \
  "feature pipelines", "model retraining", "production model governance" — \
  but ONLY where the profile's underlying work justifies the term.
- When the profile references Databricks, Kafka, or similar pipeline tools in the context \
  of ML or data workflows, surface them as workflow orchestration / pipeline orchestration \
  to address JD requirements for Airflow-style tooling.
If the JD is for a D2C, consumer health, telehealth, or subscription commerce company \
(signals: "subscription", "recurring", "D2C", "telehealth", "clinical", "health platform", \
"promotions", "catalog", "checkout"):
- For roles touching pharmacy, health, or regulated consumer data (e.g. Walgreens at \
  Cognizant), add or reframe a bullet naming the health/pharmacy domain and referencing \
  health data sensitivity or regulatory context (e.g. "pharmacy-regulated eCommerce", \
  "health data privacy controls").
- Reframe any recurring billing, auto-pay, B2B payment scheduling, or membership work \
  using subscription language: "recurring billing", "subscription billing", "recurring \
  payment infrastructure" — only where the underlying work justifies it.
- For B2C/eCommerce roles (e.g. Neiman Marcus), foreground consumer-facing outcomes: \
  conversion rate improvements, customer journey architecture, consumer UX decisions, \
  and retention-related metrics. Lead with these over infrastructure bullets.
- Surface any promotions engine, discounting logic, coupon/offer systems, A/B test \
  framework, or feature toggle work explicitly under "promotions platform" or \
  "promotions domain" framing.
- Where the JD pairs "conversion and retention" as success metrics, ensure both appear \
  in relevant experience bullets where the profile has supporting evidence.
If the JD is a healthcare, pharmacy, pharmacy benefit management (PBM), or health-tech role \
(signals: "pharmacy", "PBM", "pharmacy benefit management", "formulary", "claims", \
"healthcare", "benefits", "clinical", "health plan", "member", "payer", "provider"):
- At Cognizant (Associate Director): lead with the Walgreens engagement — frame it explicitly \
  as pharmacy benefit management platform modernization: re-engineered and cloud-native-architected \
  the pharmacy benefits and eCommerce platform for Walgreens, a leading pharmacy benefit operator. \
  Reference health data sensitivity, regulatory context (HIPAA-adjacent), and the scale of the \
  pharmacy customer base. Make this the first or second bullet in that role.
- Reframe "modernized the ecommerce platforms" for Walgreens as modernizing the \
  pharmacy benefit management and member-facing digital platform — cloud-native microservices, \
  API-first architecture, scalable benefits delivery — only where the profile's underlying \
  work justifies the framing.
- In the summary, surface the Walgreens/pharmacy domain work as a specific healthcare \
  industry credential alongside financial services credibility.
If the JD is a frontend engineering, UI platform, or developer experience role \
(signals: "frontend", "component library", "monorepo", "Angular", "TypeScript", \
"design system", "accessibility", "WCAG", "developer tooling", "UI platform", \
"micro-frontend"):
- At Neiman-Marcus Group: lead with all frontend/UI bullets — micro-frontend architecture, \
  React/TypeScript/NodeJS component development, design systems, A/B testing and feature \
  toggle frameworks, search platform modernization. Name specific UI libraries and frameworks.
- At Southern Glazers Wine & Spirits: foreground design systems, micro-frontend \
  architectures, Internal Developer Platform (IDP), A/B test and toggle frameworks, \
  AI-assisted developer tooling (GitHub Copilot, Claude Code). Frame the IDP as a \
  shared developer platform and component delivery system.
- In technical skills, ensure Angular, TypeScript, ReactJS, NodeJS, micro-frontends, \
  design systems, and CI/CD for frontend assets are prominent and listed first.
- Do NOT invent monorepo experience if the profile does not explicitly mention it; \
  surface the closest analogues (IDP, shared component platforms, design systems) instead.
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
Cloud platform ordering rule: \
- If the JD specifies GCP as the preferred or primary cloud, list GCP services FIRST \
  in the Cloud entry, before AWS and Azure.
- If the JD specifies AWS as preferred, list AWS first. \
- Default order (no preference stated): AWS, Azure, GCP.
Orchestration surface rule: \
- If the JD requires workflow orchestration tools (Apache Airflow, Cloud Composer, \
  Prefect, etc.), scan the profile for any tools that perform equivalent pipeline \
  orchestration (Databricks Workflows, Kafka-based pipelines, AWS Step Functions, \
  Azure Data Factory, etc.) and surface them explicitly under a \
  "Orchestration & Pipelines" or "Data Pipelines" skill entry. \
  Do NOT invent tools not present in the profile.
SQL visibility rule: \
- If the JD calls out SQL as a required or preferred skill, ensure "SQL" appears \
  explicitly in the skills output (in addition to any database names). \
  The profile lists Oracle, MySQL, PostgreSQL — extract "SQL" as a named skill.
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

# Maps each resume section to the profile ## headings it needs.
# Keys are normalised header slugs produced by _extract_profile_sections().
SECTION_PROFILE_SLICE: dict[str, list[str]] = {
    "meta":       [],                                               # JD only — no profile needed
    "education":  ["education", "contact"],
    "header":     ["expertise", "skills_competencies", "certifications"],
    "highlights": ["executive_summary", "professional_achievements"],
    "skills":     ["skills_competencies", "certifications"],
    "summary":    ["expertise", "executive_summary",
                   "professional_achievements", "professional_experience"],
    "experience": ["professional_experience"],
}

SECTION_CONTEXT = """\
## Candidate Profile
{profile}

## Job Description
{jd}

## Your Task
{task}
"""

# ---------------------------------------------------------------------------
# Option 2 — post-tailoring keyword audit pass
# Runs after all section agents complete; patches the top remaining gaps.
# ---------------------------------------------------------------------------

KEYWORD_AUDIT_SYSTEM = """\
You are a resume keyword auditor. You review a tailored resume against a job description \
and produce targeted, factually-grounded corrections for the most critical keyword gaps.

STRICT RULES:
1. Only use facts from the candidate profile. Do NOT invent or embellish content.
2. Return corrections for the top 5 gaps maximum — focus on highest-severity gaps only.
3. Every correction must use the JD's exact vocabulary where possible.
4. Return ONLY valid JSON — no markdown fences, no commentary.
5. NEVER mention the hiring company in any correction text.
"""

KEYWORD_AUDIT_PROMPT = """\
## Job Description
{jd}

## Current Tailored Resume Content (JSON)
{content}

## Your Task
Identify the top 5 highest-severity JD keyword gaps in the resume content above. \
The resume content already contains all available candidate facts — use only what is \
present in it. Do NOT invent content.

Return JSON:
{{
  "corrections": [
    {{
      "section": "<summary|highlights|experience|skills>",
      "company": "<exact company name if section=experience, else null>",
      "action": "<add|replace>",
      "old": "<exact existing text to replace — null if action=add>",
      "new": "<corrected or new text using JD vocabulary, grounded in resume facts>"
    }}
  ]
}}
"""


def _apply_corrections(content: dict, corrections: list) -> dict:
    import copy
    c = copy.deepcopy(content)
    for corr in corrections:
        section = corr.get("section")
        action  = corr.get("action")
        company = (corr.get("company") or "").lower()
        old     = corr.get("old")
        new     = corr.get("new")
        if not new:
            continue

        if section == "summary":
            if action == "add":
                c.setdefault("summary", []).append(new)
            elif action == "replace" and old:
                c["summary"] = [new if b == old else b for b in c.get("summary", [])]

        elif section == "highlights":
            if action == "add":
                title = new.split(":")[0].strip() if ":" in new else new[:40]
                c.setdefault("highlights", []).append({"title": title, "desc": new})
            elif action == "replace" and old:
                for h in c.get("highlights", []):
                    if h.get("desc") == old or old in h.get("title", ""):
                        h["desc"] = new
                        break

        elif section == "experience":
            for exp in c.get("experience", []):
                if company and company not in exp.get("company", "").lower():
                    continue
                if action == "add":
                    exp.setdefault("bullets", []).insert(0, new)
                elif action == "replace" and old:
                    exp["bullets"] = [new if b == old else b for b in exp.get("bullets", [])]
                break

        elif section == "skills":
            if action == "add":
                c.setdefault("technical_skills", []).append(new)
            elif action == "replace" and old:
                c["technical_skills"] = [
                    new if s == old else s for s in c.get("technical_skills", [])
                ]
    return c


def _keyword_audit(profile: str, jd: str, content: dict) -> dict:
    """Post-tailoring keyword gap analysis and targeted correction pass."""
    prompt = KEYWORD_AUDIT_PROMPT.format(
        jd=jd,
        content=json.dumps(content, indent=2),
    )
    try:
        raw         = claude_client.call(KEYWORD_AUDIT_SYSTEM, prompt)
        audit_data  = _parse_json(raw)
        corrections = audit_data.get("corrections", [])
        if corrections:
            print(f"  [audit] applying {len(corrections)} keyword correction(s)")
            content = _apply_corrections(content, corrections)
        else:
            print("  [audit] no keyword gaps found")
    except Exception as exc:
        print(f"  [warn] keyword audit failed: {exc}", file=sys.stderr)
    return content


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


def _extract_profile_sections(profile: str) -> dict[str, str]:
    """Split profile.md into named chunks keyed by normalised ## heading slug."""
    chunks: dict[str, str] = {}
    current_key = "_preamble"
    buf = ""
    for line in profile.splitlines(keepends=True):
        if line.startswith("## "):
            if buf.strip():
                chunks[current_key] = buf
            heading = line[3:].strip()
            current_key = re.sub(r"[^a-z0-9]+", "_", heading.lower()).strip("_")
            buf = line
        else:
            buf += line
    if buf.strip():
        chunks[current_key] = buf
    return chunks


def _call_section(section: str, profile_sections: dict[str, str], jd: str) -> tuple[str, dict]:
    keys = SECTION_PROFILE_SLICE.get(section, [])
    profile_slice = "\n".join(
        profile_sections[k] for k in keys if k in profile_sections
    ).strip() or "(not required for this section)"
    prompt = SECTION_CONTEXT.format(
        profile=profile_slice,
        jd=jd,
        task=SECTION_PROMPTS[section],
    )
    raw = claude_client.call(SYSTEM_PROMPT, prompt)
    return section, _parse_json(raw)


def _call_parallel(profile: str, jd: str) -> dict:
    profile_sections = _extract_profile_sections(profile)
    # Truncated JD for content sections — strips EEO/legal boilerplate
    jd_short = (jd[:6000] + "\n...[truncated]") if len(jd) > 6000 else jd
    results: dict = {}
    sections = list(SECTION_PROMPTS.keys())

    with ThreadPoolExecutor(max_workers=len(sections)) as pool:
        futures = {
            # meta gets full JD so the company name (often at the end) is never cut off
            pool.submit(_call_section, section, profile_sections,
                        jd if section == "meta" else jd_short): section
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
                    _, data = _call_section(section, profile_sections, jd)
                    results[section] = data
                    print(f"  [done] {section} (retry)")
                except Exception as exc2:
                    print(f"  [error] {section}: {exc2}", file=sys.stderr)
                    raise

    # Merge all section dicts into one flat content dict
    content = {}
    for section_data in results.values():
        content.update(section_data)

    # Post-tailoring keyword audit pass
    print("  Running keyword audit pass...")
    content = _keyword_audit(profile, jd, content)

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
    profile_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "profile.md")
    jd_text = jd_loader.load(sys.argv[1])
    result = tailor(profile_path, jd_text)
    print(json.dumps(result, indent=2))
