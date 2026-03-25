import re

import streamlit as st

from ai_helper import generate_json


_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "into", "is",
    "it", "of", "on", "or", "that", "the", "their", "this", "to", "with", "you", "your",
    "will", "can", "should", "must", "have", "has", "had", "using", "use", "used", "within",
    "across", "over", "under", "our", "we", "they", "them", "who", "what", "when", "where",
    "how", "why", "than", "then", "also", "such", "other", "ability", "abilities", "strong",
    "excellent", "good", "plus", "preferred", "requirements", "requirement", "responsibilities",
    "responsibility", "qualification", "qualifications", "including", "include", "build", "develop",
    "team", "work", "working", "role", "position", "candidate", "job", "experience",
}
_SHORT_IMPORTANT_TOKENS = {"ai", "ml", "qa", "ui", "ux", "go"}
_TECH_VOCAB = {
    "python", "java", "javascript", "typescript", "react", "node", "node.js", "sql", "nosql",
    "aws", "azure", "gcp", "docker", "kubernetes", "microservices", "apis", "api", "backend",
    "frontend", "fullstack", "full-stack", "rag", "llm", "llms", "prompt", "ai", "ml",
    "tensorflow", "pytorch", "spark", "airflow", "etl", "nlp", "azure openai", "openai", "c#",
    ".net", "asp.net", "distributed", "systems", "cloud", "search", "retrieval", "generative ai",
}
_PHRASE_ENDINGS = {
    "systems", "engineering", "engineer", "developer", "models", "model", "learning", "openai",
    "cards", "card", "mode", "services", "service", "platform", "platforms", "pipelines",
    "pipeline", "native", "architecture", "architectures", "planning", "search", "generation",
}
_DISPLAY_TOKEN_MAP = {
    "ai": "AI",
    "ml": "ML",
    "qa": "QA",
    "ui": "UI",
    "ux": "UX",
    "api": "API",
    "apis": "APIs",
    "aws": "AWS",
    "gcp": "GCP",
    "sql": "SQL",
    "nosql": "NoSQL",
    "llm": "LLM",
    "llms": "LLMs",
    "rag": "RAG",
    "c#": "C#",
    ".net": ".NET",
    "asp.net": "ASP.NET",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "node.js": "Node.js",
}
_CATEGORY_LABELS = [
    ("keyword_match", "Keyword Match"),
    ("skills_alignment", "Skills Alignment"),
    ("job_title_match", "Job Title Match"),
    ("education_fit", "Education Fit"),
    ("experience_years", "Experience Years"),
    ("format_parseability", "Format/Parseability"),
    ("domain_depth", "Domain Depth"),
]
_ATS_STYLE = """
<style>
.ats-card {
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 18px;
    padding: 1.1rem 1rem;
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.06), rgba(15, 23, 42, 0.02));
    text-align: center;
}
.ats-eyebrow {
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #64748b;
}
.ats-score {
    font-size: 3rem;
    font-weight: 800;
    margin: 0.4rem 0 0.1rem;
    line-height: 1;
}
.ats-label {
    font-size: 1rem;
    font-weight: 700;
}
.ats-chip-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.75rem;
}
.ats-chip {
    display: inline-block;
    border-radius: 999px;
    padding: 0.35rem 0.7rem;
    font-size: 0.9rem;
    font-weight: 700;
}
.ats-chip-found {
    background: rgba(34, 197, 94, 0.14);
    color: #166534;
    border: 1px solid rgba(34, 197, 94, 0.35);
}
.ats-chip-partial {
    background: rgba(245, 158, 11, 0.14);
    color: #92400e;
    border: 1px solid rgba(245, 158, 11, 0.35);
}
.ats-chip-missing {
    background: rgba(239, 68, 68, 0.14);
    color: #991b1b;
    border: 1px solid rgba(239, 68, 68, 0.35);
}
</style>
"""


def _clamp_score(value):
    return max(0, min(100, int(round(value))))


def _normalize_space(text):
    return re.sub(r"\s+", " ", (text or "").strip())


def _canonicalize_term(term):
    value = _normalize_space((term or "").lower().strip(" ,.;:|()[]{}"))
    replacements = {
        "c sharp": "c#",
        "c-sharp": "c#",
        "dot net": ".net",
        "asp net": "asp.net",
        "nodejs": "node.js",
        "node js": "node.js",
        "gen ai": "generative ai",
        "genai": "generative ai",
        "llm": "large language models",
        "llms": "large language models",
        "large language model": "large language models",
        "ai/ml": "ai ml",
        "machine-learning": "machine learning",
        "search mode": "search mode",
        "answer cards": "answer cards",
    }
    return replacements.get(value, value)


def _normalize_text_for_matching(text):
    normalized = f" {_normalize_space((text or '').lower())} "
    phrase_replacements = [
        ("c sharp", "c#"),
        ("c-sharp", "c#"),
        ("dot net", ".net"),
        ("asp net", "asp.net"),
        ("node js", "node.js"),
        ("nodejs", "node.js"),
        ("gen ai", "generative ai"),
        ("genai", "generative ai"),
        ("large language model", "large language models"),
        ("llm", "large language models"),
        ("llms", "large language models"),
        ("ai/ml", "ai ml"),
    ]
    for old, new in phrase_replacements:
        normalized = normalized.replace(f" {old} ", f" {new} ")
    normalized = re.sub(r"[^a-z0-9+#./\s-]", " ", normalized)
    return f" {_normalize_space(normalized)} "


def _is_meaningful_token(token):
    if not token or token in _STOPWORDS:
        return False
    if token in _SHORT_IMPORTANT_TOKENS:
        return True
    if re.search(r"[+#./]|\d", token):
        return True
    return len(token) >= 3


def _is_meaningful_phrase(phrase):
    tokens = [token for token in phrase.split() if token]
    if not tokens:
        return False
    if len(tokens) == 1:
        return _is_meaningful_token(tokens[0])
    if all(token in _STOPWORDS for token in tokens):
        return False
    if tokens[0] in _STOPWORDS or tokens[-1] in _STOPWORDS:
        return False
    return True


def _display_term(term):
    parts = []
    for token in term.split():
        if token in _DISPLAY_TOKEN_MAP:
            parts.append(_DISPLAY_TOKEN_MAP[token])
        elif token in {"and", "of", "for", "to", "on"}:
            parts.append(token)
        else:
            parts.append(token.capitalize())
    return " ".join(parts)


def _dedupe_keep_order(items):
    seen = set()
    ordered = []
    for item in items:
        key = item.lower() if isinstance(item, str) else str(item)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(item)
    return ordered


def _extract_candidate_terms(text, max_terms=18):
    scores = {}

    def add_term(raw_term, weight):
        term = _canonicalize_term(raw_term)
        if not _is_meaningful_phrase(term):
            return
        if len(term) < 2:
            return
        scores[term] = scores.get(term, 0) + weight

    for raw in re.findall(r"[A-Za-z0-9][A-Za-z0-9+#./-]*", text or ""):
        canonical_raw = _canonicalize_term(raw)
        if canonical_raw in _TECH_VOCAB or canonical_raw in _SHORT_IMPORTANT_TOKENS:
            base_weight = 1.8
        elif re.search(r"[+#./]|\d", raw):
            base_weight = 1.2
        else:
            base_weight = 0.35
        add_term(raw, base_weight)

    for segment in re.split(r"[\n,;|()•]+", text or ""):
        tokens = [
            _canonicalize_term(token)
            for token in re.findall(r"[A-Za-z0-9+#./-]+", segment.lower())
        ]
        tokens = [token for token in tokens if _is_meaningful_token(token)]
        for length, weight in ((3, 3.2), (2, 2.2), (1, 1.0)):
            if len(tokens) < length:
                continue
            for index in range(len(tokens) - length + 1):
                phrase_tokens = tokens[index:index + length]
                tech_token_count = sum(1 for token in phrase_tokens if token in _TECH_VOCAB)
                if length >= 3 and tech_token_count >= 2:
                    continue
                if length == 2 and tech_token_count == 2 and phrase_tokens[-1] not in _PHRASE_ENDINGS:
                    continue
                phrase = " ".join(phrase_tokens)
                if not _is_meaningful_phrase(phrase):
                    continue
                bonus = 0.0
                if any(re.search(r"[+#./]|\d", token) for token in phrase_tokens):
                    bonus += 0.9
                if any(token in _TECH_VOCAB for token in phrase_tokens):
                    bonus += 0.45
                add_term(phrase, weight + bonus)

    ranked = sorted(scores.items(), key=lambda item: (-item[1], -len(item[0]), item[0]))
    return [_display_term(term) for term, _ in ranked[:max_terms]]


def _classify_keyword_hits(jd_text, resume_text, max_terms=18):
    candidate_terms = _extract_candidate_terms(jd_text, max_terms=max_terms)
    normalized_resume = _normalize_text_for_matching(resume_text)
    found = []
    partial = []
    missing = []

    for display_term in candidate_terms:
        canonical_term = _canonicalize_term(display_term)
        if f" {canonical_term} " in normalized_resume:
            found.append(display_term)
            continue

        tokens = [token for token in canonical_term.split() if token and token not in _STOPWORDS]
        matched_tokens = 0
        for token in tokens:
            if re.search(rf"\b{re.escape(token)}\b", normalized_resume):
                matched_tokens += 1

        if len(tokens) > 1 and matched_tokens == len(tokens):
            partial.append(display_term)
        elif len(tokens) > 1 and matched_tokens >= 1:
            partial.append(display_term)
        elif matched_tokens and matched_tokens * 5 >= len(tokens) * 3:
            partial.append(display_term)
        else:
            missing.append(display_term)

    return {
        "found": found,
        "partial": partial,
        "missing": missing,
        "all_terms": candidate_terms,
    }


def _extract_target_role(jd_text):
    for line in [line.strip() for line in (jd_text or "").splitlines() if line.strip()][:12]:
        match = re.search(
            r"((?:senior|staff|lead|principal|junior|jr\.?|sr\.?|associate)\s+){0,2}"
            r"([A-Za-z/&+-]+(?:\s+[A-Za-z/&+-]+){0,3}\s+(?:engineer|developer|scientist|manager|architect|analyst|consultant|specialist|designer))",
            line,
            flags=re.IGNORECASE,
        )
        if match:
            return _normalize_space(match.group(0))
    return ""


def _extract_required_years(jd_text):
    years = []
    for match in re.finditer(r"(\d+)\s*(?:\+|plus)?\s*(?:to|-)?\s*(\d+)?\s+years", jd_text or "", flags=re.IGNORECASE):
        lower = int(match.group(1))
        upper = int(match.group(2)) if match.group(2) else lower
        years.append(max(lower, upper))
    return max(years) if years else 0


def _estimate_resume_years(resume_text):
    years = [int(year) for year in re.findall(r"\b(19\d{2}|20\d{2})\b", resume_text or "")]
    if not years:
        return 0
    earliest = min(years)
    latest = 2026 if re.search(r"\b(present|current)\b", resume_text or "", flags=re.IGNORECASE) else max(years)
    return max(0, min(30, latest - earliest))


def _estimate_job_title_match(jd_text, resume_text):
    role = _extract_target_role(jd_text)
    if not role:
        return 75, ""

    normalized_resume = _normalize_text_for_matching(resume_text)
    role_canonical = _canonicalize_term(role)
    if f" {role_canonical} " in normalized_resume:
        return 100, role

    role_tokens = [token for token in role_canonical.split() if token not in _STOPWORDS and token not in {"senior", "staff", "lead", "principal", "associate", "jr", "sr"}]
    if not role_tokens:
        return 75, role

    matched = sum(1 for token in role_tokens if re.search(rf"\b{re.escape(token)}\b", normalized_resume))
    score = 30 + (matched / len(role_tokens)) * 60
    return _clamp_score(score), role


def _estimate_education_fit(jd_text, resume_text):
    jd_lower = (jd_text or "").lower()
    resume_lower = (resume_text or "").lower()
    requirement_map = {
        "phd": {"phd", "doctorate"},
        "masters": {"master", "masters", "m.s", "msc", "mba"},
        "bachelors": {"bachelor", "bachelors", "b.s", "bs", "btech", "b.e", "bachelor's"},
    }

    required_level = ""
    if re.search(r"\b(phd|doctorate)\b", jd_lower):
        required_level = "phd"
    elif re.search(r"\b(master|masters|m\.s|msc|mba)\b", jd_lower):
        required_level = "masters"
    elif re.search(r"\b(bachelor|bachelors|b\.s|bs|btech|b\.e)\b", jd_lower):
        required_level = "bachelors"

    if not required_level:
        return 90

    if any(token in resume_lower for token in requirement_map[required_level]):
        return 100
    if re.search(r"\b(education|university|college|degree|bachelor|master|phd)\b", resume_lower):
        return 65
    return 35


def _estimate_format_parseability(resume_text):
    word_count = len(re.findall(r"\b\w+\b", resume_text or ""))
    bullets = len(re.findall(r"(?m)^\s*[•\-*]", resume_text or ""))
    section_hits = len(
        {
            section.lower()
            for section in re.findall(
                r"\b(Summary|Skills|Experience|Projects|Education|Certifications|Awards|Publications|Languages)\b",
                resume_text or "",
                flags=re.IGNORECASE,
            )
        }
    )
    score = 45
    if 250 <= word_count <= 1400:
        score += 20
    elif word_count >= 160:
        score += 10
    score += min(section_hits * 6, 24)
    score += min(bullets * 2, 16)
    if re.search(r"\b(email|phone|linkedin)\b", resume_text or "", flags=re.IGNORECASE):
        score += 8
    return _clamp_score(score)


def _score_from_buckets(found_count, partial_count, total_count):
    if not total_count:
        return 0
    return _clamp_score(((found_count + partial_count * 0.5) / total_count) * 100)


def _looks_technical(term):
    canonical = _canonicalize_term(term)
    if re.search(r"[+#./]|\d", canonical):
        return True
    return any(token in _TECH_VOCAB for token in canonical.split())


def _build_local_strengths(category_scores, keyword_hits, role_name):
    strengths = []
    if category_scores["keyword_match"] >= 80:
        strengths.append("Strong overlap with the job description's primary keywords.")
    if category_scores["skills_alignment"] >= 75:
        strengths.append("Core tools and technical skills line up well with the target role.")
    if category_scores["format_parseability"] >= 80:
        strengths.append("Resume text appears ATS-readable with recognizable sections and good structure.")
    if role_name and category_scores["job_title_match"] >= 75:
        strengths.append(f"Your resume already signals relevance to the target role: {role_name}.")
    if not strengths and keyword_hits["found"]:
        strengths.append(f"You already match important JD terms such as {', '.join(keyword_hits['found'][:3])}.")
    return strengths[:4]


def _build_local_weaknesses(category_scores, keyword_hits, role_name, required_years, resume_years):
    weaknesses = []
    if keyword_hits["missing"]:
        weaknesses.append(f"Key JD terms are still missing: {', '.join(keyword_hits['missing'][:4])}.")
    if role_name and category_scores["job_title_match"] < 70:
        weaknesses.append(f"The resume does not clearly mirror the target title: {role_name}.")
    if required_years and resume_years < required_years:
        weaknesses.append(f"Years-of-experience signal looks lighter than the JD's preferred {required_years}+ years.")
    if category_scores["format_parseability"] < 70:
        weaknesses.append("Formatting and section labeling may make ATS parsing less reliable.")
    if category_scores["education_fit"] < 70:
        weaknesses.append("Education requirement is not obvious in the extracted resume text.")
    return weaknesses[:4]


def _build_improvement_recommendations(keyword_hits, category_scores, role_name, required_years, resume_years):
    recommendations = []
    for term in keyword_hits["missing"][:3]:
        recommendations.append(f"Add one concrete bullet or project that explicitly mentions '{term}' if that experience is real.")
    for term in keyword_hits["partial"][:2]:
        recommendations.append(f"Turn partial alignment on '{term}' into an exact phrase in your skills or experience bullets.")
    if role_name and category_scores["job_title_match"] < 75:
        recommendations.append(f"Mirror the target role title '{role_name}' in your summary or most relevant experience entry if accurate.")
    if required_years and resume_years < required_years:
        recommendations.append(
            f"Strengthen the years-of-experience signal; the JD asks for about {required_years}+ years and your resume reads lighter than that today."
        )
    if category_scores["format_parseability"] < 75:
        recommendations.append("Use standard section headers, simple bullets, and clean dates so ATS parsing remains reliable.")
    if category_scores["education_fit"] < 75:
        recommendations.append("Make your degree or education line more explicit if the job requires a named credential.")
    return _dedupe_keep_order(recommendations)[:6]


def _build_rewrite_priorities(keyword_hits, role_name):
    priorities = []
    for term in keyword_hits["missing"][:3]:
        priorities.append(f"Add explicit proof for {term}.")
    for term in keyword_hits["partial"][:2]:
        priorities.append(f"Rewrite one bullet to directly include {term}.")
    if role_name:
        priorities.append(f"Tighten the summary to align with {role_name}.")
    return _dedupe_keep_order(priorities)[:5]


def _normalize_ai_list(data, key):
    value = data.get(key, []) if isinstance(data, dict) else []
    if isinstance(value, list):
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]
    return []


def _generate_ai_enrichment(resume_text, jd_text, local_report):
    system_instruction = """
    You are an expert ATS parser and technical recruiter.
    Return STRICT JSON only with this schema:
    {
        "strengths": ["string"],
        "weaknesses": ["string"],
        "rewrite_priorities": ["string"],
        "rewritten_bullets": ["string"],
        "actionable_suggestions": ["string"]
    }
    Keep every item concise, specific, and truthful.
    """
    prompt = f"""
    JOB DESCRIPTION:
    {jd_text}

    RESUME TEXT:
    {resume_text}

    LOCAL ATS FINDINGS:
    - Overall score: {local_report['score']}
    - Missing keywords: {', '.join(local_report['keyword_hits']['missing'][:8])}
    - Partial keywords: {', '.join(local_report['keyword_hits']['partial'][:8])}
    - Improvement recommendations: {' | '.join(local_report['improvement_recommendations'][:6])}
    """
    try:
        data = generate_json(prompt, system_instruction=system_instruction, fallback={})
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _build_ats_report(resume_text, jd_text):
    keyword_hits = _classify_keyword_hits(jd_text, resume_text)
    total_keywords = max(len(keyword_hits["all_terms"]), 1)
    technical_terms = [term for term in keyword_hits["all_terms"] if _looks_technical(term)]
    technical_found = [term for term in keyword_hits["found"] if term in technical_terms]
    technical_partial = [term for term in keyword_hits["partial"] if term in technical_terms]
    multiword_terms = [term for term in technical_terms if len(term.split()) > 1]
    multiword_found = [term for term in technical_found if term in multiword_terms]
    multiword_partial = [term for term in technical_partial if term in multiword_terms]
    keyword_match = _score_from_buckets(len(keyword_hits["found"]), len(keyword_hits["partial"]), total_keywords)
    skills_alignment = _score_from_buckets(len(technical_found), len(technical_partial), max(len(technical_terms), 1))
    domain_depth = _score_from_buckets(len(multiword_found), len(multiword_partial), max(len(multiword_terms), 1))
    job_title_match, role_name = _estimate_job_title_match(jd_text, resume_text)
    education_fit = _estimate_education_fit(jd_text, resume_text)
    required_years = _extract_required_years(jd_text)
    resume_years = _estimate_resume_years(resume_text)
    experience_years = _clamp_score((resume_years / required_years) * 100) if required_years else (80 if resume_years >= 2 else 60)
    format_parseability = _estimate_format_parseability(resume_text)
    category_scores = {
        "keyword_match": keyword_match,
        "skills_alignment": skills_alignment,
        "job_title_match": job_title_match,
        "education_fit": education_fit,
        "experience_years": experience_years,
        "format_parseability": format_parseability,
        "domain_depth": domain_depth,
    }
    overall_score = _clamp_score(
        keyword_match * 0.24
        + skills_alignment * 0.18
        + job_title_match * 0.14
        + education_fit * 0.10
        + experience_years * 0.12
        + format_parseability * 0.10
        + domain_depth * 0.12
    )
    match_label = "Excellent Match" if overall_score >= 90 else "Strong Match" if overall_score >= 80 else "Good Match" if overall_score >= 70 else "Partial Match" if overall_score >= 60 else "Needs Work"
    return {
        "score": overall_score,
        "match_label": match_label,
        "keyword_hits": {"found": keyword_hits["found"], "partial": keyword_hits["partial"], "missing": keyword_hits["missing"]},
        "score_breakdown": {
            "keyword_match": keyword_match,
            "technical_alignment": _clamp_score((skills_alignment + domain_depth) / 2),
            "impact_strength": format_parseability,
            "experience_alignment": _clamp_score((job_title_match + experience_years + education_fit) / 3),
        },
        "category_scores": [{"key": key, "label": label, "score": category_scores[key]} for key, label in _CATEGORY_LABELS],
        "missing_keywords": keyword_hits["missing"],
        "missing_tools": [term for term in keyword_hits["missing"] if _looks_technical(term)][:6],
        "missing_domain_terms": [term for term in keyword_hits["missing"] if len(term.split()) > 1][:6],
        "strengths": _build_local_strengths(category_scores, keyword_hits, role_name),
        "weaknesses": _build_local_weaknesses(category_scores, keyword_hits, role_name, required_years, resume_years),
        "rewrite_priorities": _build_rewrite_priorities(keyword_hits, role_name),
        "rewritten_bullets": [],
        "improvement_recommendations": _build_improvement_recommendations(keyword_hits, category_scores, role_name, required_years, resume_years),
        "actionable_suggestions": [],
        "target_role": role_name,
        "required_years": required_years,
        "estimated_resume_years": resume_years,
    }


def _merge_reports(local_report, ai_report):
    merged = dict(local_report)
    merged["strengths"] = _dedupe_keep_order(local_report["strengths"] + _normalize_ai_list(ai_report, "strengths"))[:5]
    merged["weaknesses"] = _dedupe_keep_order(local_report["weaknesses"] + _normalize_ai_list(ai_report, "weaknesses"))[:5]
    merged["rewrite_priorities"] = _dedupe_keep_order(local_report["rewrite_priorities"] + _normalize_ai_list(ai_report, "rewrite_priorities"))[:6]
    merged["rewritten_bullets"] = _dedupe_keep_order(_normalize_ai_list(ai_report, "rewritten_bullets"))[:4]
    merged["actionable_suggestions"] = _dedupe_keep_order(local_report["improvement_recommendations"] + _normalize_ai_list(ai_report, "actionable_suggestions"))[:8]
    return merged


def get_resume_score(resume_text, jd_text):
    local_report = _build_ats_report(resume_text, jd_text)
    ai_report = _generate_ai_enrichment(resume_text, jd_text, local_report)
    return _merge_reports(local_report, ai_report)


def render_ats_report(results):
    st.markdown(_ATS_STYLE, unsafe_allow_html=True)
    st.markdown("---")
    st.header("📈 Analysis Results")
    score = results.get("score", 0)
    score_color = "#16a34a" if score >= 80 else "#d97706" if score >= 60 else "#dc2626"
    summary_col, category_col = st.columns([1, 2])
    with summary_col:
        st.markdown(
            (
                "<div class='ats-card'>"
                "<div class='ats-eyebrow'>Overall ATS Score</div>"
                f"<div class='ats-score' style='color:{score_color};'>{score}</div>"
                "<div style='font-size:0.95rem; color:#64748b;'>/100</div>"
                f"<div class='ats-label' style='color:{score_color};'>{results.get('match_label', 'Match')}</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )
    with category_col:
        st.subheader("Score By Category")
        for item in results.get("category_scores", []):
            label_col, bar_col, value_col = st.columns([2.6, 5.5, 1])
            label_col.markdown(f"**{item['label']}**")
            bar_col.progress(item["score"] / 100)
            value_col.markdown(f"**{item['score']}%**")
    st.subheader("Keyword Hits")
    keyword_hits = results.get("keyword_hits", {})
    for title, terms, status_class, empty_text in [
        ("Found in resume", keyword_hits.get("found", []), "ats-chip-found", "No strong keyword matches yet."),
        ("Partial signal", keyword_hits.get("partial", []), "ats-chip-partial", "No partial matches detected."),
        ("Missing from resume", keyword_hits.get("missing", []), "ats-chip-missing", "No major gaps detected."),
    ]:
        st.markdown(f"**{title}**")
        if not terms:
            st.caption(empty_text)
        else:
            chips = "".join([f"<span class='ats-chip {status_class}'>{term}</span>" for term in terms])
            st.markdown(f"<div class='ats-chip-wrap'>{chips}</div>", unsafe_allow_html=True)
    recommendations = results.get("improvement_recommendations", [])
    if recommendations:
        st.subheader("What Would Push You Higher")
        for index, item in enumerate(recommendations, start=1):
            st.markdown(f"{index}. {item}")