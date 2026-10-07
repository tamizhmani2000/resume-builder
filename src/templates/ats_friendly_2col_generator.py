#!/usr/bin/env python3
"""Generator for the ats-friendly.pdf template.

Paired template: templates/ats-friendly.pdf
Layout mirrors the ats-friendly.pdf template:
  • Full-width header  (name · gold tagline · contact)
  • Left column ~61%   (Summary, Experience)
  • Right column ~39%  (Achievements, Competencies, Technology, Certs, Education)
  • Both columns continue on page 2 if content overflows

Accepts an optional `content` dict from jd_tailor.py for JD-tailored output.
When content=None the hardcoded base profile is used (default behavior).
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Paragraph, HRFlowable, Table, TableStyle
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.platypus import Frame

import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))


def _output_path(content=None):
    if content and content.get("meta"):
        company = content["meta"].get("company", "")
        slug    = content["meta"].get("role_slug", "")
        parts   = [p for p in [company.replace(" ", "_"), slug.replace("-", "_")] if p]
        suffix  = ("_" + "_".join(parts)) if parts else ""
        fname   = f"TJ_Tamilmani_Jayaraman_Resume{suffix}.pdf"
    else:
        fname = "TJ_Tamilmani_Jayaraman_Resume.pdf"
    return _os.path.join(_HERE, "..", "..", "output", fname)


# ── Page geometry ─────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = letter          # 612 × 792 pt
MX  = 0.55 * inch                # horizontal margin
MT  = 0.50 * inch                # top margin
MB  = 0.50 * inch                # bottom margin
CW  = PAGE_W - 2 * MX           # usable content width

HDR_H   = 1.15 * inch           # header block height (sized for 2-line taglines)
HDR_GAP = 0.10 * inch

# Body region on page 1
BODY_TOP_Y = PAGE_H - MT - HDR_H - HDR_GAP   # y of top of body
BODY_H_P1  = BODY_TOP_Y - MB                  # height of body on page 1

# Body region on page 2+
BODY_TOP_Y2 = PAGE_H - MT - 0.20 * inch       # leave room for continuation label
BODY_H_P2   = BODY_TOP_Y2 - MB

# Two-column split
COL_GAP = 0.15 * inch
L_W = CW * 0.608
R_W = CW - L_W - COL_GAP
L_X = MX
R_X = MX + L_W + COL_GAP

# ── Color palette ─────────────────────────────────────────────────────────────
GOLD = colors.HexColor("#C49A3C")
DARK = colors.HexColor("#1A1A1A")
GRAY = colors.HexColor("#6B6B6B")
RULE = colors.HexColor("#CCCCCC")


# ── Paragraph styles ──────────────────────────────────────────────────────────
def _s(**kw):
    name = kw.pop("_n", "s")
    return ParagraphStyle(name, **kw)

ST = dict(
    name    = _s(_n="name",   fontName="Helvetica-Bold",       fontSize=24, textColor=DARK, leading=28, spaceAfter=2),
    tagline = _s(_n="tl",     fontName="Helvetica-Bold",       fontSize=11, textColor=GOLD, leading=14, spaceAfter=3),
    contact = _s(_n="ct",     fontName="Helvetica",            fontSize=9,  textColor=GRAY, leading=12),
    cont_lbl= _s(_n="cl",     fontName="Helvetica",            fontSize=8,  textColor=GRAY, leading=10),
    sec     = _s(_n="sec",    fontName="Helvetica-Bold",       fontSize=8,  textColor=GRAY, leading=10, spaceBefore=8, spaceAfter=1),
    jtitle  = _s(_n="jt",     fontName="Helvetica-Bold",       fontSize=10, textColor=DARK, leading=13, spaceBefore=6, spaceAfter=0),
    co      = _s(_n="co",     fontName="Helvetica-Bold",       fontSize=9,  textColor=GOLD, leading=11, spaceAfter=0),
    dates   = _s(_n="dt",     fontName="Helvetica",            fontSize=8,  textColor=GRAY, leading=10, spaceAfter=2),
    bul_dot = _s(_n="bdt",    fontName="Helvetica",            fontSize=8.5,textColor=DARK, leading=12),
    bul     = _s(_n="bul",    fontName="Helvetica",            fontSize=8.5,textColor=DARK, leading=12),
    ach_t   = _s(_n="at",     fontName="Helvetica-Bold",       fontSize=9,  textColor=DARK, leading=11, spaceBefore=5, spaceAfter=1),
    ach_b   = _s(_n="ab",     fontName="Helvetica",            fontSize=8.5,textColor=DARK, leading=12, spaceAfter=4),
    sk_v    = _s(_n="sv",     fontName="Helvetica",            fontSize=8.5,textColor=DARK, leading=12, spaceAfter=3),
    edu_d   = _s(_n="ed",     fontName="Helvetica-Bold",       fontSize=9,  textColor=DARK, leading=11, spaceBefore=3, spaceAfter=0),
    edu_i   = _s(_n="ei",     fontName="Helvetica",            fontSize=8,  textColor=GOLD, leading=10, spaceAfter=3),
)


# ── Helpers ───────────────────────────────────────────────────────────────────
def sec(title):
    return [
        Paragraph(title.upper(), ST["sec"]),
        HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=4),
    ]

def b(text, col_width=None):
    dot = Paragraph("•", ST["bul_dot"])
    txt = Paragraph(text, ST["bul"])
    cw = col_width or 300
    t = Table([[dot, txt]],
              colWidths=[8, cw - 8],
              style=TableStyle([
                  ("LEFTPADDING",  (0, 0), (-1, -1), 0),
                  ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                  ("TOPPADDING",   (0, 0), (-1, -1), 0),
                  ("BOTTOMPADDING",(0, 0), (-1, -1), 2),
                  ("VALIGN",       (0, 0), (-1, -1), "TOP"),
              ]))
    return t

def frame(x, y_bottom, w, h, lpad=0, rpad=0):
    return Frame(x, y_bottom, w, h,
                 leftPadding=lpad, rightPadding=rpad,
                 topPadding=0, bottomPadding=0)

def _html_escape(text):
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("&lt;b&gt;", "<b>")
            .replace("&lt;/b&gt;", "</b>"))


# ── Base profile data ─────────────────────────────────────────────────────────
BASE = dict(
    tagline = (
        "Digital Engineering  |  Cloud Infrastructure  |  "
        "DevSecOps  |  Platform Engineering  |  AI/ML"
    ),
    summary = [
        "Strategic Technology Leader with 20+ years of experience leading enterprise-scale digital transformations and cloud modernization.",
        "Expert in building high-performance engineering cultures and delivering robust cloud foundations from ground zero to global production.",
        "Proven track record aligning technical roadmaps with business objectives — specializing in Digital Transformation, Cloud Engineering, FinOps Governance, DevSecOps Automation, and 99.99% system resiliency for multi-billion-dollar platforms.",
    ],
    highlights = [
        ("Cloud Foundation at Scale",
         "Architected and deployed enterprise Cloud Foundation Platform in 12 weeks, enabling rapid multi-BU adoption."),
        ("Application Modernization",
         "Modernized legacy commerce application into scalable, cloud-native microservice architecture, improving agility and reducing time-to-market."),
        ("99.99% Platform Availability",
         "Drove 35% MTTR reduction and 99.99% uptime for the $4B SGWS e-commerce platform via SRE transformation."),
        ("AI &amp; GenAI Adoption",
         "Deployed Gen AI tools, RAG pipelines, and MCP agentic frameworks enterprise-wide, measurably boosting sales productivity."),
        ("FinOps Governance",
         "Established automated cloud governance workflows, driving fiscal accountability and material cloud cost reduction."),
        ("$30M Portfolio Leadership",
         "Managed $30M annual delivery portfolio at Cognizant — consistent on-time, on-budget delivery for Fortune 500 clients."),
        ("Vendor &amp; Cost Optimization",
         "Negotiated multi-year contracts &gt;$5M/year; strategic procurement achieving substantial toolchain cost savings."),
    ],
    jobs = [
        (
            "Director – Digital Engineering",
            "Southern Glazers Wine &amp; Spirits",
            "May 2021 – Present  ·  Dallas, TX",
            [
                "Architected and executed comprehensive IT and cloud strategies scaling high-volume B2B commerce platforms to 24/7 global reliability.",
                "Led cross-functional rollout of CDN, IAM, and observability platforms, standardizing the enterprise technology stack.",
                "Negotiated multi-year vendor contracts exceeding $5M/year; managed $3M annual talent and staffing portfolio.",
                "Pioneered AI-driven operational excellence integrating foundational models and agentic workflows (RAG, MCP), boosting sales team productivity.",
                "Orchestrated organizational pivot from reactive AMS to proactive SRE — driving 35% MTTR reduction and 99.99% availability for $4B e-commerce platform.",
                "Championed FinOps maturity and transparent cloud governance; provided M&amp;A technical due diligence.",
                "Strategic advisor to C-suite, aligning technology roadmaps with enterprise investment planning and long-term business objectives.",
            ],
        ),
        (
            "Principal Engineer &amp; Platform Leader",
            "Neiman Marcus Group",
            "Oct 2018 – May 2021  ·  Dallas, TX",
            [
                "Directed SRE and DevOps teams, standardizing methodologies and observability toolsets for global luxury retail platforms.",
                "Directed CDN transformation and mission-critical system upgrades to optimize the global digital footprint.",
                "Implemented rigorous capacity planning and rightsizing, driving significant cloud cost savings.",
                "Pioneered RPA and Microservices automation (Java / Spring Boot) to eliminate toil and accelerate engineering velocity.",
                "Architected and scaled cloud-native AWS ecosystems (Serverless, Fargate, EC2) for high-availability enterprise infrastructure.",
            ],
        ),
        (
            "Associate Director – Engineering",
            "Cognizant",
            "Apr 2010 – Aug 2018",
            [
                "Partnered with C-suite to scale digital commerce for Fortune 500 retail, driving enterprise adoption of Agile and DevOps.",
                "Managed $30M annual delivery portfolio; oversaw financial forecasts and KPIs across global programs.",
                "Built international Centers of Excellence (CoE) to standardize multi-regional delivery and foster cross-functional innovation.",
                "Led Waterfall to Agile (SAFe / Scrum / Kanban) and DevOps transformation; established TRAIN delivery framework.",
            ],
        ),
        (
            "Manager – Engineering &amp; Projects",
            "Atos Origin",
            "Oct 2009 – Apr 2010",
            [
                "Directed cross-continental teams delivering scalable automotive platforms for the Renault-Nissan Alliance.",
                "Spearheaded modular SOA architectures, significantly accelerating time-to-market for digital features.",
            ],
        ),
        (
            "Director – Technology",
            "Mahindra Satyam",
            "Jan 2007 – Oct 2009",
            [
                "Managed multimillion-dollar project budgets for Ford and the World Bank, ensuring profitability and optimal resource allocation.",
                "Championed engineering excellence and mentorship programs, significantly increasing employee retention.",
            ],
        ),
        (
            "Principal / Technology Lead",
            "Cognizant",
            "Sep 2002 – Jan 2007",
            [
                "Designed and implemented loan underwriting applications for AMEX (Java, J2EE, MQ, WebLogic).",
                "Designed customer service application for Chase Credit Card division (Visual Basic, Java, Oracle).",
            ],
        ),
        (
            "Programmer",
            "Altosys Technologies",
            "Oct 2000 – Sep 2002",
            [
                "Developed client-server applications using Visual Basic, Oracle, MTS, and ASP.",
                "Designed application and database architecture, ER diagrams.",
            ],
        ),
        (
            "Software Engineer",
            "Kaashyap Radiant Systems",
            "Mar 1999 – Sep 2000",
            [
                "Designed and built client-server applications using Visual Basic and Oracle.",
            ],
        ),
    ],
    competencies = (
        "Cloud Strategy &amp; Governance · Enterprise Digital Transformation · "
        "DevSecOps &amp; Automation · FinOps &amp; Cost Optimization · "
        "SRE &amp; Observability · AI/ML &amp; GenAI · "
        "M&amp;A Due Diligence · Global Team Leadership · Vendor Negotiation"
    ),
    technical_skills = [
        "<b>Cloud:</b> AWS (EC2, EKS, Fargate, S3, Lambda, API Gateway, DynamoDB, ALB, Route53, SQS, Kinesis, CloudFormation, Bedrock) · Azure (AKS, Cosmos DB, Service Bus, Event Grid, Functions)",
        "<b>IaC &amp; DevOps:</b> Terraform · CloudFormation · GitHub Actions · Kubernetes · Docker",
        "<b>Languages:</b> Java · JavaScript · TypeScript · Python",
        "<b>Frameworks:</b> ReactJS · Spring",
        "<b>Security:</b> Network · Infrastructure · Data · Cloud · Pipeline · Layer 7 · Fraud Detection &amp; Monitoring · IAM · IDP · CDN",
        "<b>Platforms:</b> Kubernetes · Docker · SAP Hybris · ATG",
        "<b>Data &amp; AI:</b> GenAI · RAG · Agentic Frameworks · LangChain · LangGraph · Crew AI · Claude · Deep Learning · Neural Networks · CNN · NLP",
        "<b>Architecture:</b> Cloud-Native · Microservices · SOA · GraphQL · REST · SOAP",
        "<b>Delivery:</b> Agile · Scrum · Kanban",
    ],
    certifications = [
        "AWS Certified Solution Architect",
        "Project Management Professional (PMP)",
        "Certified Scrum Master",
        "Sun Certified Java Programmer",
        "Microsoft Certified Professional",
    ],
    education = [
        ("Post Graduate Program – AI &amp; Machine Learning", "UT Austin  ·  2026"),
        ("Executive Program – Business Management", "IIM Calcutta, India  ·  2011"),
        ("Masters in Computer Applications", "Madurai Kamaraj University, India  ·  2001"),
        ("Bachelor of Science", "Madras University, India  ·  1997"),
    ],
)


def _resolve(content):
    """Return (tagline, summary, highlights, jobs, competencies, technical_skills, certifications, education)."""
    if not content:
        return (BASE["tagline"], BASE["summary"], BASE["highlights"], BASE["jobs"],
                BASE["competencies"], BASE["technical_skills"], BASE["certifications"], BASE["education"])

    tagline      = content.get("tagline", BASE["tagline"])
    summary      = content.get("summary", BASE["summary"])
    raw_hl       = content.get("highlights", [])
    highlights   = [(h["title"], h["desc"]) for h in raw_hl] if raw_hl else BASE["highlights"]
    raw_exp      = content.get("experience", [])
    jobs         = [(e["title"], e["company"], e["dates"], e["bullets"]) for e in raw_exp] if raw_exp else BASE["jobs"]
    competencies = content.get("competencies", BASE["competencies"])
    raw_skills   = content.get("technical_skills", [])
    technical_skills = raw_skills if raw_skills else BASE["technical_skills"]
    certifications   = content.get("certifications", BASE["certifications"])
    raw_edu          = content.get("education", [])
    education        = [(e["degree"], e["institution"]) for e in raw_edu] if raw_edu else BASE["education"]
    return tagline, summary, highlights, jobs, competencies, technical_skills, certifications, education


# ── Content builders ──────────────────────────────────────────────────────────
def build_header(tagline):
    return [
        Paragraph("TAMILMANI JAYARAMAN (TJ)", ST["name"]),
        Paragraph(tagline, ST["tagline"]),
        Paragraph(
            "Dallas, TX  ·  tamizhmani2000@gmail.com  ·  "
            "(201) 290-9366  ·  https://www.linkedin.com/in/tamizh",
            ST["contact"]),
        HRFlowable(width="100%", thickness=1.2, color=GOLD, spaceAfter=0),
    ]


def build_left(summary, jobs, content=None):
    fl = []
    lw = L_W - 6

    fl += sec("Summary")
    for s in summary:
        fl.append(b(_html_escape(s) if content else s, lw))

    fl += sec("Experience")
    for title, company, dates, bullets in jobs:
        t = _html_escape(title)   if content else title
        c = _html_escape(company) if content else company
        fl.append(Paragraph(t, ST["jtitle"]))
        fl.append(Paragraph(c, ST["co"]))
        fl.append(Paragraph(dates, ST["dates"]))
        for bt in bullets:
            fl.append(b(_html_escape(bt) if content else bt, lw))

    return fl


def build_right(highlights, competencies, technical_skills, certifications, education, content=None):
    fl = []
    rw = R_W - 4

    fl += sec("Professional Highlights")
    for title, desc in highlights:
        t = _html_escape(title) if content else title
        d = _html_escape(desc)  if content else desc
        fl.append(Paragraph(t, ST["ach_t"]))
        fl.append(Paragraph(d, ST["ach_b"]))

    fl += sec("Core Competencies")
    fl.append(Paragraph(
        _html_escape(competencies) if content else competencies,
        ST["sk_v"]))

    fl += sec("Technical Skills")
    for line in technical_skills:
        fl.append(Paragraph(_html_escape(line) if content else line, ST["sk_v"]))

    fl += sec("Certifications")
    for cert in certifications:
        fl.append(b(_html_escape(cert) if content else cert, rw))

    fl += sec("Education")
    for deg, inst in education:
        fl.append(Paragraph(_html_escape(deg) if content else deg, ST["edu_d"]))
        fl.append(Paragraph(_html_escape(inst) if content else inst, ST["edu_i"]))

    return fl


# ── PDF assembly ──────────────────────────────────────────────────────────────
def build(content=None):
    out = _output_path(content)
    tagline, summary, highlights, jobs, competencies, technical_skills, certifications, education = _resolve(content)

    c = pdf_canvas.Canvas(out, pagesize=letter)

    hdr   = build_header(tagline)
    left  = build_left(summary, jobs, content)
    right = build_right(highlights, competencies, technical_skills, certifications, education, content)

    first_page = True

    while left or right:
        if not first_page:
            c.showPage()
            lbl_frame = frame(L_X, PAGE_H - MT - 0.18 * inch, CW, 0.18 * inch)
            lbl_frame.addFromList(
                [Paragraph("TAMILMANI JAYARAMAN (TJ)", ST["cont_lbl"])], c)
            body_h = BODY_H_P2
            body_bottom = MB
        else:
            hdr_frame = frame(L_X, PAGE_H - MT - HDR_H, CW, HDR_H)
            hdr_frame.addFromList(hdr, c)
            body_h = BODY_H_P1
            body_bottom = MB
            first_page = False

        lf = frame(L_X, body_bottom, L_W, body_h, rpad=6)
        lf.addFromList(left, c)

        rf = frame(R_X, body_bottom, R_W, body_h, lpad=4)
        rf.addFromList(right, c)

    c.save()
    print(f"Resume saved: {out}")
    return out


if __name__ == "__main__":
    build()
