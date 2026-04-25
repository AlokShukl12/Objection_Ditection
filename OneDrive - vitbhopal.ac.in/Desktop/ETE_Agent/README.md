# AI-Powered Talent Scouting & Engagement Agent

An interactive recruiter assistant that:

- parses a Job Description (JD),
- discovers matching candidates,
- scores explainable fit (`Match Score`),
- simulates outreach conversations to estimate intent (`Interest Score`),
- outputs a ranked shortlist with actionable detail.

## Features

- JD parsing for role, skills, experience, location, work model, compensation, and domain signals.
- Explainable matching with score breakdown:
  - skills,
  - experience,
  - location,
  - work-model fit,
  - domain fit.
- Conversational outreach simulation (candidate transcript generation).
- Interest scoring from positive/negative engagement signals.
- Combined ranking using configurable weight between `Match` and `Interest`.
- Streamlit UI with candidate-level transparency and CSV export.

## Project Structure

```text
.
|-- app.py
|-- agent.py
|-- requirements.txt
|-- README.md
`-- data/
    `-- candidates.json
```

## Quick Start

1. Create and activate a virtual environment (recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run app:

```bash
streamlit run app.py
```

4. Open the local URL printed by Streamlit.

## How to Use

1. Paste a JD in the text box or click `Load Sample JD`.
2. Configure:
   - discovery pool size,
   - final shortlist size,
   - `Match Score` weight.
3. Optionally upload your own candidate JSON list.
4. Click `Run Scouting Agent`.
5. Review:
   - parsed JD summary,
   - ranked shortlist table,
   - per-candidate explanation and transcript.
6. Export shortlist via `Download Shortlist CSV`.

## Candidate JSON Schema

Each candidate object should include:

- `candidate_id` (string)
- `name` (string)
- `title` (string)
- `location` (string)
- `years_experience` (number)
- `skills` (string array)
- `domains` (string array)
- `preferred_work_model` (`remote` | `hybrid` | `onsite`)
- `expected_ctc_lpa` (number)
- `notice_period_days` (number)
- `intent_baseline` (0.0 to 1.0)
- `motivators` (string array)
- `blockers` (string array)

## Notes

- Outreach is simulated and deterministic per candidate/JD combination for demo consistency.
- The scoring model is heuristic and explainable; you can tune weights and formulas in `agent.py`.
