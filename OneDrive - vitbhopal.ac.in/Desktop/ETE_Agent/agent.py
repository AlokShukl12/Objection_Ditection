from __future__ import annotations

import hashlib
import json
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SKILL_CATALOG = [
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "node.js",
    "node",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "terraform",
    "spark",
    "hadoop",
    "airflow",
    "machine learning",
    "deep learning",
    "nlp",
    "llm",
    "genai",
    "langchain",
    "fastapi",
    "django",
    "flask",
    "pytorch",
    "tensorflow",
    "scikit-learn",
    "tableau",
    "power bi",
    "excel",
    "git",
    "ci/cd",
    "redis",
    "kafka",
    "microservices",
]

DOMAIN_CATALOG = [
    "fintech",
    "healthcare",
    "edtech",
    "saas",
    "ecommerce",
    "cybersecurity",
    "logistics",
    "manufacturing",
    "retail",
    "telecom",
]

LOCATION_HINTS = [
    "bangalore",
    "bengaluru",
    "hyderabad",
    "pune",
    "mumbai",
    "delhi",
    "gurugram",
    "chennai",
    "noida",
    "remote",
]


def _clean_token(token: str) -> str:
    return token.strip().lower()


def _extract_keywords(text: str, catalog: list[str]) -> list[str]:
    text_l = text.lower()
    hits = []
    for item in catalog:
        pattern = r"\b" + re.escape(item.lower()) + r"\b"
        if re.search(pattern, text_l):
            hits.append(item)
    return sorted(set(hits))


def _bounded(score: float, floor: float = 0.0, ceil: float = 100.0) -> float:
    return max(floor, min(ceil, score))


@dataclass
class JDParseResult:
    title: str
    raw_text: str
    must_have_skills: list[str]
    good_to_have_skills: list[str]
    min_experience_years: int | None
    max_experience_years: int | None
    location: str | None
    work_model: str | None
    min_ctc_lpa: int | None
    max_ctc_lpa: int | None
    domains: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "must_have_skills": self.must_have_skills,
            "good_to_have_skills": self.good_to_have_skills,
            "min_experience_years": self.min_experience_years,
            "max_experience_years": self.max_experience_years,
            "location": self.location,
            "work_model": self.work_model,
            "min_ctc_lpa": self.min_ctc_lpa,
            "max_ctc_lpa": self.max_ctc_lpa,
            "domains": self.domains,
        }


class TalentScoutingAgent:
    def __init__(self, candidates: list[dict[str, Any]]) -> None:
        self.candidates = candidates

    def parse_jd(self, jd_text: str) -> JDParseResult:
        text = jd_text.strip()
        if not text:
            raise ValueError("Job description is empty.")

        lines = [line.strip(" -\t") for line in text.splitlines() if line.strip()]
        title = lines[0] if lines else "Untitled Role"
        lower = text.lower()

        range_match = re.search(r"(\d{1,2})\s*[-to]+\s*(\d{1,2})\s*(?:\+?\s*)?(?:years|yrs)", lower)
        explicit_years = re.findall(r"(\d{1,2})\s*\+?\s*(?:years|yrs)", lower)
        min_exp = None
        max_exp = None
        if range_match:
            min_exp = int(range_match.group(1))
            max_exp = int(range_match.group(2))
        elif explicit_years:
            min_exp = int(explicit_years[0])

        ctc_range = re.search(r"(\d{1,3})\s*[-to]+\s*(\d{1,3})\s*(?:lpa|lakhs?)", lower)
        ctc_single = re.search(r"(\d{1,3})\s*\+?\s*(?:lpa|lakhs?)", lower)
        min_ctc = None
        max_ctc = None
        if ctc_range:
            min_ctc = int(ctc_range.group(1))
            max_ctc = int(ctc_range.group(2))
        elif ctc_single:
            min_ctc = int(ctc_single.group(1))

        work_model = None
        if "remote" in lower and "hybrid" in lower:
            work_model = "hybrid"
        elif "remote" in lower:
            work_model = "remote"
        elif "hybrid" in lower:
            work_model = "hybrid"
        elif "onsite" in lower or "on-site" in lower:
            work_model = "onsite"

        location = None
        for hint in LOCATION_HINTS:
            if hint in lower:
                location = hint
                break
        if not location:
            location_match = re.search(r"(?:location|based in)\s*[:\-]?\s*([a-zA-Z ]{3,30})", lower)
            if location_match:
                location = location_match.group(1).strip().lower()

        must_lines = []
        good_lines = []
        for line in lines:
            ll = line.lower()
            if any(word in ll for word in ["must", "required", "mandatory"]):
                must_lines.append(line)
            if any(word in ll for word in ["good to have", "nice to have", "preferred", "plus"]):
                good_lines.append(line)

        all_skills = _extract_keywords(text, SKILL_CATALOG)
        must_skills = _extract_keywords(" ".join(must_lines), SKILL_CATALOG)
        good_skills = _extract_keywords(" ".join(good_lines), SKILL_CATALOG)
        if not must_skills:
            must_skills = all_skills[: min(7, len(all_skills))]
        if not good_skills:
            good_skills = [skill for skill in all_skills if skill not in must_skills]

        domains = _extract_keywords(text, DOMAIN_CATALOG)

        return JDParseResult(
            title=title,
            raw_text=text,
            must_have_skills=must_skills,
            good_to_have_skills=good_skills,
            min_experience_years=min_exp,
            max_experience_years=max_exp,
            location=location,
            work_model=work_model,
            min_ctc_lpa=min_ctc,
            max_ctc_lpa=max_ctc,
            domains=domains,
        )

    def _score_match(self, candidate: dict[str, Any], jd: JDParseResult) -> dict[str, Any]:
        candidate_skills = [_clean_token(s) for s in candidate.get("skills", [])]
        must = [_clean_token(s) for s in jd.must_have_skills]
        good = [_clean_token(s) for s in jd.good_to_have_skills]

        must_overlap = sorted(set(candidate_skills).intersection(set(must)))
        good_overlap = sorted(set(candidate_skills).intersection(set(good)))

        if must:
            must_score = 100 * (len(must_overlap) / len(must))
        else:
            must_score = 60
        if good:
            good_score = 100 * (len(good_overlap) / len(good))
        else:
            good_score = 50
        skill_score = 0.78 * must_score + 0.22 * good_score

        exp_score = 75.0
        years_exp = candidate.get("years_experience", 0)
        if jd.min_experience_years is not None:
            if years_exp >= jd.min_experience_years:
                overshoot = years_exp - jd.min_experience_years
                exp_score = _bounded(100 - min(overshoot * 2.5, 17))
            else:
                gap = jd.min_experience_years - years_exp
                exp_score = _bounded(100 - gap * 20, floor=20)
        if jd.max_experience_years is not None and years_exp > jd.max_experience_years:
            exp_score = _bounded(exp_score - (years_exp - jd.max_experience_years) * 8, floor=10)

        candidate_location = candidate.get("location", "").lower()
        location_score = 70.0
        if jd.location:
            if jd.location in candidate_location or candidate_location in jd.location:
                location_score = 100.0
            elif jd.work_model in {"remote", "hybrid"}:
                location_score = 84.0
            else:
                location_score = 45.0

        candidate_work_model = candidate.get("preferred_work_model", "hybrid").lower()
        work_model_score = 80.0
        if jd.work_model:
            if jd.work_model == candidate_work_model:
                work_model_score = 100.0
            elif jd.work_model == "hybrid" and candidate_work_model in {"remote", "onsite"}:
                work_model_score = 72.0
            elif jd.work_model == "remote" and candidate_work_model == "hybrid":
                work_model_score = 88.0
            elif jd.work_model == "onsite" and candidate_work_model == "hybrid":
                work_model_score = 84.0
            else:
                work_model_score = 44.0

        candidate_domains = [_clean_token(d) for d in candidate.get("domains", [])]
        jd_domains = [_clean_token(d) for d in jd.domains]
        domain_overlap = sorted(set(candidate_domains).intersection(set(jd_domains)))
        domain_score = 72.0
        if jd_domains:
            domain_score = 100 * (len(domain_overlap) / len(jd_domains))

        match_score = _bounded(
            (skill_score * 0.5)
            + (exp_score * 0.2)
            + (location_score * 0.1)
            + (domain_score * 0.1)
            + (work_model_score * 0.1)
        )

        explanations = [
            f"Must-have skill overlap: {len(must_overlap)}/{len(must)}",
            f"Good-to-have skill overlap: {len(good_overlap)}/{len(good)}",
            f"Experience fit: {years_exp} years vs requirement {jd.min_experience_years or 'not specified'}",
            f"Domain overlap: {', '.join(domain_overlap) if domain_overlap else 'none'}",
        ]

        return {
            "candidate_id": candidate["candidate_id"],
            "name": candidate["name"],
            "title": candidate["title"],
            "location": candidate["location"],
            "match_score": round(match_score, 2),
            "score_breakdown": {
                "skill_score": round(skill_score, 2),
                "experience_score": round(exp_score, 2),
                "location_score": round(location_score, 2),
                "domain_score": round(domain_score, 2),
                "work_model_score": round(work_model_score, 2),
            },
            "skill_matches": {
                "must_overlap": must_overlap,
                "good_overlap": good_overlap,
            },
            "explanations": explanations,
            "profile": candidate,
        }

    def discover_and_match(self, jd: JDParseResult, candidate_pool_size: int = 15) -> list[dict[str, Any]]:
        scored = [self._score_match(candidate, jd) for candidate in self.candidates]
        scored.sort(key=lambda c: c["match_score"], reverse=True)
        return scored[:candidate_pool_size]

    def _generate_candidate_reply(self, interest_score: float, name: str, tone: str) -> tuple[str, str]:
        if interest_score >= 75:
            first = (
                f"Hi, thanks for reaching out. This sounds close to what I want next, "
                f"and I am open to discuss immediately."
            )
            second = (
                "Could you share interview stages and expected impact in the first 90 days?"
            )
            return first, second
        if interest_score >= 50:
            first = (
                "Thanks for sharing. I am interested in learning more, "
                "especially around role scope and flexibility."
            )
            second = "Please share the team setup and compensation range before I commit to interviews."
            return first, second
        first = (
            "I appreciate the message. At this point the role may not align with my priorities, "
            "but I am open to revisit later."
        )
        second = "If there is flexibility on model or scope, you can circle back in a few months."
        return first, second

    def simulate_outreach(self, scored_candidates: list[dict[str, Any]], jd: JDParseResult, tone: str) -> list[dict[str, Any]]:
        enriched = []
        jd_lower = jd.raw_text.lower()
        for item in scored_candidates:
            candidate = item["profile"]

            seed_base = f"{candidate['candidate_id']}::{jd.title}::{jd.min_experience_years}"
            seed_int = int(hashlib.md5(seed_base.encode("utf-8")).hexdigest()[:8], 16)
            rng = random.Random(seed_int)

            positive_signals = []
            negative_signals = []

            for motivator in candidate.get("motivators", []):
                if motivator.lower() in jd_lower:
                    positive_signals.append(f"JD mentions motivator: {motivator}")

            for blocker in candidate.get("blockers", []):
                if blocker.lower() not in jd_lower:
                    negative_signals.append(f"Potential blocker not addressed in JD: {blocker}")

            if jd.max_ctc_lpa and candidate.get("expected_ctc_lpa", 0) > jd.max_ctc_lpa:
                negative_signals.append(
                    f"Compensation mismatch: expects {candidate.get('expected_ctc_lpa')} LPA"
                )

            if jd.work_model and candidate.get("preferred_work_model") != jd.work_model:
                if not (jd.work_model == "remote" and candidate.get("preferred_work_model") == "hybrid"):
                    negative_signals.append(
                        f"Work-model mismatch: prefers {candidate.get('preferred_work_model')}"
                    )

            notice_days = candidate.get("notice_period_days", 60)
            if notice_days > 90:
                negative_signals.append(f"Long notice period: {notice_days} days")

            base_intent = float(candidate.get("intent_baseline", 0.5)) * 42
            interest_score = (
                base_intent
                + (item["match_score"] * 0.48)
                + (len(positive_signals) * 8)
                - (len(negative_signals) * 9)
                + rng.uniform(-4.0, 4.0)
            )
            interest_score = round(_bounded(interest_score), 2)

            first_reply, second_reply = self._generate_candidate_reply(interest_score, item["name"], tone)

            opener = (
                f"Hi {item['name']}, I am hiring for {jd.title}. "
                f"Your background in {', '.join(candidate.get('skills', [])[:3])} stood out. "
                "Would you be open to a 15-minute discussion this week?"
            )
            follow_up = (
                f"Thanks for the response. This role is {jd.work_model or 'flexible model'} "
                f"and focused on {', '.join(jd.must_have_skills[:3]) or 'core engineering delivery'}."
            )
            closer = (
                "Understood. I will share the formal JD and next steps so you can decide comfortably."
            )

            transcript = [
                {"speaker": "Recruiter", "message": opener},
                {"speaker": "Candidate", "message": first_reply},
                {"speaker": "Recruiter", "message": follow_up},
                {"speaker": "Candidate", "message": second_reply},
                {"speaker": "Recruiter", "message": closer},
            ]

            enriched.append(
                {
                    **item,
                    "interest_score": interest_score,
                    "interest_signals": {
                        "positive": positive_signals or ["Strong skill alignment from profile"],
                        "negative": negative_signals,
                    },
                    "transcript": transcript,
                    "outreach_tone": tone,
                }
            )
        return enriched

    def rank_shortlist(
        self,
        engaged_candidates: list[dict[str, Any]],
        match_weight: float = 0.65,
        interest_weight: float = 0.35,
        shortlist_size: int = 8,
    ) -> list[dict[str, Any]]:
        if match_weight + interest_weight == 0:
            match_weight = 0.5
            interest_weight = 0.5
        total = match_weight + interest_weight
        mw = match_weight / total
        iw = interest_weight / total

        final = []
        for item in engaged_candidates:
            combined = round((item["match_score"] * mw) + (item["interest_score"] * iw), 2)
            final.append({**item, "combined_score": combined})
        final.sort(key=lambda c: c["combined_score"], reverse=True)
        return final[:shortlist_size]


def load_candidates_from_json(path: str | Path) -> list[dict[str, Any]]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("Candidate file must contain a JSON list.")
    return data
