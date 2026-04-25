from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from agent import TalentScoutingAgent, load_candidates_from_json


DEFAULT_JD = """Senior Applied AI Engineer - Talent Intelligence
Location: Bangalore (Hybrid)
Experience: 4-7 years
Compensation: 24-40 LPA

We are building an AI-powered talent intelligence platform for enterprise recruiting.
Must have:
- Strong Python and SQL fundamentals
- Hands-on experience with LLM, NLP, and machine learning systems
- Production API development with FastAPI or similar
- Cloud deployment experience on AWS/GCP

Good to have:
- LangChain or agentic workflow experience
- Docker/Kubernetes exposure
- Fintech or SaaS domain background

You will own end-to-end delivery, collaborate with product leaders, and mentor junior engineers.
"""


JD_TEMPLATES = {
    "Applied AI Engineer": DEFAULT_JD,
    "Data Platform Engineer": """Data Platform Engineer
Location: Hyderabad (Hybrid)
Experience: 5-8 years
Compensation: 22-35 LPA

Must have:
- Python and SQL at production scale
- Spark, Airflow, and distributed data pipelines
- AWS with Terraform and CI/CD
- Strong ownership mindset

Good to have:
- Kafka and streaming systems
- Fintech or healthcare data exposure
- Team mentorship experience
""",
    "Full Stack Product Engineer": """Senior Full Stack Engineer
Location: Remote
Experience: 4-7 years
Compensation: 18-30 LPA

Must have:
- TypeScript, React, Node.js
- PostgreSQL and API design
- Docker and cloud deployment experience

Good to have:
- SaaS domain experience
- Product analytics mindset
- Experience mentoring junior engineers
""",
}


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&display=swap');

            :root {
                --bg-0: #f2f6f9;
                --bg-1: #e6eef4;
                --ink-0: #0f2433;
                --ink-1: #2c4355;
                --brand-0: #0f6c8d;
                --brand-1: #1f8e9b;
                --accent-0: #ff8f3f;
                --card: rgba(255, 255, 255, 0.9);
                --stroke: rgba(20, 46, 67, 0.14);
                --good: #127a4f;
                --bad: #a02a2a;
            }

            html, body, [class*="css"]  {
                font-family: "Sora", sans-serif;
                color: var(--ink-0);
            }

            .stApp {
                background:
                    radial-gradient(circle at 6% 8%, #d7ecf8 0%, transparent 38%),
                    radial-gradient(circle at 92% 5%, #ffe8d4 0%, transparent 38%),
                    linear-gradient(180deg, var(--bg-0), var(--bg-1));
            }

            .hero-shell {
                border: 1px solid var(--stroke);
                background: linear-gradient(120deg, #ffffffd9 0%, #f7fbffd9 100%);
                border-radius: 18px;
                padding: 18px 20px;
                box-shadow: 0 20px 36px -28px rgba(10, 30, 45, 0.52);
                margin-bottom: 10px;
            }

            .hero-kicker {
                letter-spacing: 0.08em;
                font-size: 12px;
                color: var(--brand-0);
                font-weight: 700;
                text-transform: uppercase;
            }

            .hero-title {
                margin-top: 2px;
                font-size: 30px;
                line-height: 1.15;
                font-weight: 700;
                color: var(--ink-0);
            }

            .hero-sub {
                margin-top: 6px;
                color: var(--ink-1);
                font-size: 14px;
            }

            .badge-row {
                margin-top: 12px;
            }

            .badge-pill {
                display: inline-block;
                padding: 6px 12px;
                border-radius: 999px;
                margin-right: 8px;
                margin-bottom: 8px;
                font-size: 12px;
                font-weight: 600;
                color: #ffffff;
                background: linear-gradient(110deg, var(--brand-0), var(--brand-1));
            }

            .ui-card {
                border: 1px solid var(--stroke);
                border-radius: 14px;
                background: var(--card);
                padding: 14px;
            }

            .rank-chip {
                display: inline-block;
                border-radius: 8px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.05em;
                color: #fff;
                background: linear-gradient(120deg, #134d67, #0f8e8e);
            }

            .subtle {
                color: #4b6376;
                font-size: 13px;
            }

            .skill-chip {
                display: inline-block;
                margin-right: 7px;
                margin-bottom: 7px;
                padding: 4px 10px;
                border-radius: 999px;
                border: 1px solid #d6e3ed;
                color: #234458;
                background: #f7fbff;
                font-size: 12px;
                font-weight: 600;
            }

            .signal-good {
                color: var(--good);
                font-weight: 600;
                margin-bottom: 6px;
                font-size: 13px;
            }

            .signal-bad {
                color: var(--bad);
                font-weight: 600;
                margin-bottom: 6px;
                font-size: 13px;
            }

            [data-testid="stMetric"] {
                border: 1px solid var(--stroke);
                border-radius: 14px;
                background: #ffffffc4;
                padding: 8px 10px;
            }

            @media (max-width: 900px) {
                .hero-title {
                    font-size: 24px;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def _load_default_candidates() -> list[dict[str, Any]]:
    return load_candidates_from_json(Path("data/candidates.json"))


def _load_candidates_from_upload(uploaded_file) -> list[dict[str, Any]]:
    payload = json.load(uploaded_file)
    if not isinstance(payload, list):
        raise ValueError("Uploaded JSON should be a list of candidate objects.")
    return payload


def _format_table(shortlist: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for idx, item in enumerate(shortlist, start=1):
        rows.append(
            {
                "Rank": idx,
                "Candidate": item["name"],
                "Title": item["title"],
                "Location": item["location"],
                "Work Model": item["profile"].get("preferred_work_model", "-"),
                "Match Score": item["match_score"],
                "Interest Score": item["interest_score"],
                "Combined Score": item["combined_score"],
                "Must Skills Matched": len(item["skill_matches"]["must_overlap"]),
            }
        )
    return pd.DataFrame(rows)


def _status_badge(result: dict[str, Any] | None) -> str:
    if not result:
        return "Waiting for run"
    run_meta = result.get("run_meta", {})
    return f"Last run: {run_meta.get('run_at', '-')}"


def _render_hero(result: dict[str, Any] | None) -> None:
    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-kicker">Recruiter Workspace</div>
            <div class="hero-title">AI-Powered Talent Scouting and Engagement</div>
            <div class="hero-sub">Parse JD -> Match candidates -> Simulate outreach -> Rank by fit and intent.</div>
            <div class="badge-row">
                <span class="badge-pill">{_status_badge(result)}</span>
                <span class="badge-pill">Explainable scoring</span>
                <span class="badge-pill">Conversational interest simulation</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_parsed_snapshot(parsed: dict[str, Any]) -> None:
    must = parsed["must_have_skills"] or []
    good = parsed["good_to_have_skills"] or []
    domains = parsed["domains"] or []

    left, right = st.columns(2)
    with left:
        st.markdown("#### Parsed JD Snapshot")
        st.markdown(
            f"""
            <div class="ui-card">
                <div><b>Role:</b> {parsed['title']}</div>
                <div><b>Experience:</b> {parsed['min_experience_years'] or '-'} to {parsed['max_experience_years'] or '-'}</div>
                <div><b>Location:</b> {parsed['location'] or 'Not specified'}</div>
                <div><b>Work Model:</b> {parsed['work_model'] or 'Not specified'}</div>
                <div><b>Compensation:</b> {parsed['min_ctc_lpa'] or '-'} to {parsed['max_ctc_lpa'] or '-'} LPA</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown("#### Skill and Domain Signals")
        st.markdown('<div class="ui-card">', unsafe_allow_html=True)
        st.write("Must-have")
        if must:
            st.markdown("".join([f'<span class="skill-chip">{skill}</span>' for skill in must]), unsafe_allow_html=True)
        else:
            st.caption("None extracted")
        st.write("Good-to-have")
        if good:
            st.markdown("".join([f'<span class="skill-chip">{skill}</span>' for skill in good]), unsafe_allow_html=True)
        else:
            st.caption("None extracted")
        st.write("Domain tags")
        if domains:
            st.markdown("".join([f'<span class="skill-chip">{domain}</span>' for domain in domains]), unsafe_allow_html=True)
        else:
            st.caption("None extracted")
        st.markdown("</div>", unsafe_allow_html=True)


def _filter_shortlist(
    shortlist: list[dict[str, Any]],
    min_combined: float,
    location_filter: str,
    model_filter: str,
) -> list[dict[str, Any]]:
    out = []
    for item in shortlist:
        if item["combined_score"] < min_combined:
            continue
        if location_filter != "All" and item["location"].lower() != location_filter.lower():
            continue
        model = item["profile"].get("preferred_work_model", "")
        if model_filter != "All" and model.lower() != model_filter.lower():
            continue
        out.append(item)
    return out


def _render_candidate_card(item: dict[str, Any], rank: int) -> None:
    with st.container(border=True):
        st.markdown(f'<span class="rank-chip">Rank #{rank}</span>', unsafe_allow_html=True)
        st.markdown(f"### {item['name']}")
        st.markdown(f"<div class='subtle'>{item['title']} • {item['location']}</div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Match", f"{item['match_score']:.2f}")
        c2.metric("Interest", f"{item['interest_score']:.2f}")
        c3.metric("Combined", f"{item['combined_score']:.2f}")

        st.caption("Score composition")
        st.progress(int(round(item["match_score"])), text=f"Match: {item['match_score']:.2f}")
        st.progress(int(round(item["interest_score"])), text=f"Interest: {item['interest_score']:.2f}")

        st.caption("Matched skills")
        skill_bits = item["skill_matches"]["must_overlap"] + item["skill_matches"]["good_overlap"]
        if skill_bits:
            st.markdown(
                "".join([f'<span class="skill-chip">{s}</span>' for s in skill_bits[:10]]),
                unsafe_allow_html=True,
            )
        else:
            st.caption("No explicit overlap captured from extracted skills")

        with st.expander("Explainability details"):
            for reason in item["explanations"]:
                st.write(f"- {reason}")
            st.json(item["score_breakdown"])


def _render_conversation(item: dict[str, Any]) -> None:
    st.markdown(f"### Conversation: {item['name']}")
    left, right = st.columns(2)
    with left:
        st.markdown("#### Positive signals")
        for sig in item["interest_signals"]["positive"]:
            st.markdown(f"<div class='signal-good'>+ {sig}</div>", unsafe_allow_html=True)
    with right:
        st.markdown("#### Risk signals")
        negatives = item["interest_signals"]["negative"]
        if negatives:
            for sig in negatives:
                st.markdown(f"<div class='signal-bad'>- {sig}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='signal-good'>+ No obvious blockers detected</div>", unsafe_allow_html=True)

    st.markdown("#### Simulated Outreach Transcript")
    for turn in item["transcript"]:
        role = "assistant" if turn["speaker"] == "Recruiter" else "user"
        avatar = "🧭" if role == "assistant" else "👤"
        with st.chat_message(role, avatar=avatar):
            st.write(turn["message"])


def main() -> None:
    st.set_page_config(
        page_title="AI Talent Scouting Agent",
        page_icon=":mag:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _inject_styles()

    if "jd_text" not in st.session_state:
        st.session_state["jd_text"] = DEFAULT_JD
    if "result" not in st.session_state:
        st.session_state["result"] = None

    result = st.session_state.get("result")
    _render_hero(result)

    with st.sidebar:
        st.header("Control Tower")
        st.caption("Tune ranking and outreach behavior.")

        shortlist_size = st.slider("Final shortlist size", min_value=3, max_value=15, value=8, step=1)
        pool_size = st.slider("Discovery pool size", min_value=5, max_value=18, value=12, step=1)

        match_weight_percent = st.slider(
            "Match Score Weight (%)",
            min_value=40,
            max_value=90,
            value=65,
            step=5,
        )
        interest_weight_percent = 100 - match_weight_percent
        st.caption(f"Interest Score Weight: {interest_weight_percent}%")

        outreach_tone = st.selectbox(
            "Outreach style",
            options=["consultative", "direct", "mission-led"],
            index=0,
        )
        uploaded = st.file_uploader(
            "Optional candidate JSON",
            type=["json"],
            help="If omitted, bundled sample candidate data is used.",
        )
        if st.button("Reset Results", use_container_width=True):
            st.session_state["result"] = None
            st.rerun()

    editor_col, action_col = st.columns([2.2, 1.0], gap="large")

    with editor_col:
        chosen_template = st.selectbox("JD Template", list(JD_TEMPLATES.keys()))
        template_col1, template_col2 = st.columns(2)
        with template_col1:
            if st.button("Apply Selected Template", use_container_width=True):
                st.session_state["jd_text"] = JD_TEMPLATES[chosen_template]
        with template_col2:
            if st.button("Load Original Sample", use_container_width=True):
                st.session_state["jd_text"] = DEFAULT_JD

        jd_input = st.text_area(
            "Job Description",
            key="jd_text",
            height=320,
            help="Paste a full JD. The agent will parse requirements and rank candidates.",
        )

    with action_col:
        st.markdown("#### Run Agent")
        st.markdown('<div class="ui-card">', unsafe_allow_html=True)
        st.write("1. Parse JD")
        st.write("2. Discover + score")
        st.write("3. Simulate outreach")
        st.write("4. Rank shortlist")
        run_clicked = st.button("Run Scouting Agent", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if run_clicked:
        try:
            candidates = _load_candidates_from_upload(uploaded) if uploaded else _load_default_candidates()
            agent = TalentScoutingAgent(candidates=candidates)

            with st.status("Agent execution in progress...", expanded=True) as status:
                st.write("1/4 Parsing JD requirements")
                parsed = agent.parse_jd(jd_input)
                st.write("2/4 Discovering and scoring candidate matches")
                matched = agent.discover_and_match(parsed, candidate_pool_size=pool_size)
                st.write("3/4 Simulating outreach conversations")
                engaged = agent.simulate_outreach(matched, parsed, tone=outreach_tone)
                st.write("4/4 Ranking final shortlist")
                shortlist = agent.rank_shortlist(
                    engaged,
                    match_weight=match_weight_percent / 100.0,
                    interest_weight=interest_weight_percent / 100.0,
                    shortlist_size=shortlist_size,
                )
                status.update(label="Agent run completed", state="complete")

            st.session_state["result"] = {
                "parsed": parsed.to_dict(),
                "shortlist": shortlist,
                "run_meta": {
                    "run_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tone": outreach_tone,
                    "pool_size": pool_size,
                    "shortlist_size": shortlist_size,
                    "match_weight": match_weight_percent,
                    "interest_weight": interest_weight_percent,
                },
            }
            st.rerun()
        except Exception as exc:
            st.error(f"Agent run failed: {exc}")

    result = st.session_state.get("result")
    if not result:
        st.info("Configure the JD and click 'Run Scouting Agent' to generate a ranked shortlist.")
        return

    parsed = result["parsed"]
    shortlist = result["shortlist"]
    table = _format_table(shortlist)

    tabs = st.tabs(["Overview", "Shortlist Board", "Conversations", "Exports"])

    with tabs[0]:
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Candidates Ranked", len(shortlist))
        k2.metric("Avg Match", f"{table['Match Score'].mean():.2f}")
        k3.metric("Avg Interest", f"{table['Interest Score'].mean():.2f}")
        k4.metric("Top Combined", f"{table['Combined Score'].max():.2f}")

        _render_parsed_snapshot(parsed)

        st.markdown("#### Top Candidates Snapshot")
        st.dataframe(
            table.head(5),
            use_container_width=True,
            hide_index=True,
            height=240,
        )

    with tabs[1]:
        locations = ["All"] + sorted({item["location"] for item in shortlist})
        models = ["All"] + sorted({item["profile"].get("preferred_work_model", "-") for item in shortlist})

        f1, f2, f3, f4 = st.columns(4)
        with f1:
            min_combined = st.slider("Min Combined Score", min_value=0, max_value=100, value=55, step=1)
        with f2:
            location_filter = st.selectbox("Location", locations)
        with f3:
            model_filter = st.selectbox("Work Model", models)
        with f4:
            sort_by = st.selectbox(
                "Sort By",
                ["Combined Score", "Match Score", "Interest Score"],
                index=0,
            )

        filtered = _filter_shortlist(shortlist, min_combined, location_filter, model_filter)
        key_map = {
            "Combined Score": "combined_score",
            "Match Score": "match_score",
            "Interest Score": "interest_score",
        }
        filtered.sort(key=lambda x: x[key_map[sort_by]], reverse=True)
        st.caption(f"Showing {len(filtered)} candidate(s) after filters.")

        if not filtered:
            st.warning("No candidates match current filters.")
        else:
            for rank, item in enumerate(filtered, start=1):
                _render_candidate_card(item, rank)

    with tabs[2]:
        names = [f"{item['name']} ({item['combined_score']:.2f})" for item in shortlist]
        selected_name = st.selectbox("Select Candidate", names)
        selected_idx = names.index(selected_name)
        _render_conversation(shortlist[selected_idx])

    with tabs[3]:
        st.markdown("#### Export and Operational View")
        st.dataframe(table, use_container_width=True, hide_index=True)

        col_csv, col_json = st.columns(2)
        with col_csv:
            st.download_button(
                "Download Shortlist CSV",
                data=table.to_csv(index=False).encode("utf-8"),
                file_name="ranked_shortlist.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col_json:
            st.download_button(
                "Download Full JSON",
                data=json.dumps(result, indent=2).encode("utf-8"),
                file_name="shortlist_with_explanations.json",
                mime="application/json",
                use_container_width=True,
            )

        st.markdown("#### Run Configuration")
        st.json(result.get("run_meta", {}))


if __name__ == "__main__":
    main()
