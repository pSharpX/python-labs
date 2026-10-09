# TechDoc UI — Streamlit client

A chat interface for presales teams. It only talks to the FastAPI backend (no agents or LangGraph here); the backend is the source of truth for workflow state, approvals and documents.

![Approval](/docs/screenshots/approval.png)

## Run

```bash
cd techdoc-ui
uv venv && source .venv/bin/activate
make sync
cp .env.example .env          # PS_API_BASE_URL, identity, timeouts
make serve          # http://localhost:8501
```

## Features

- **Sidebar** — start a proposal (title, customer, business need) and switch between your proposals (status icons).
- **Stepper** — Requirements → Technical design → Financial estimate → Approval → Document, with versions, blocked/active states and "needs regeneration" when a change invalidates downstream work.
- **Conversation** — the full backend message log (questions, updates, decisions). Use the chat box to answer questions or change scope at any stage.
- **Approval panel** — total, effort, duration, key assumptions; Approve / Request changes (feedback required) / Reject (reason required) / Cancel. Decisions are sent with the estimate version, so a stale screen can't approve a newer estimate.
- **Document panel** — download the approved `.docx`, with earlier versions kept.
- **Tabs** — structured requirements, solution (classification, architecture, phases, profiles, risks, Microsoft Learn references), estimate (by phase/profile/activity, formula, assumptions) and version/approval history.
- **Progress and errors** — background runs are polled with a status indicator; failures show friendly messages with trace references, and Retry where it makes sense.
- **Session restore** — the active proposal id is kept in the URL (`?proposal=…`), so refresh/reconnect returns to it (after re-checking access with the backend).

## Configuration (`PS_` prefix)

| Variable | Default | Purpose |
|---|---|---|
| `PS_API_BASE_URL` | `http://localhost:8000` | Backend URL |
| `PS_API_TIMEOUT_SECONDS` | `30` | HTTP timeout per request |
| `PS_AUTH_MODE` | `dev` | `dev` sends `X-User-Id`; `api_key` sends `Authorization: Bearer` |
| `PS_USER_ID` / `PS_API_KEY` | `dev-user` / — | Identity |
| `PS_POLL_INTERVAL_SECONDS` / `PS_POLL_TIMEOUT_SECONDS` | `1.5` / `300` | Background-run polling |
| `PS_APP_TITLE` | `Proposal Studio` | UI title |

Theme colours are in `.streamlit/config.toml` and `styles/theme.css`.

## Structure

```
app.py                 page layout and actions
api/client.py          HTTP client: auth headers, timeouts, idempotency keys, error mapping, response validation, polling
api/schemas.py         response models
state.py               session init + URL-based restore (pure, unit-tested)
components/            sidebar, chat, workflow_status, requirements_view, technical_proposal_view,
                       financial_estimate_view, approval_panel, document_panel, format
styles/theme.css
tests/                 client error handling, session restoration, stepper logic
```

## Tests

```bash
pytest -q
```
