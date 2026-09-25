# Credit Assistant

An AI-driven platform to help users understand, track, and improve their credit health
within the Indian financial ecosystem — built with **FastAPI** (backend) and **React** (frontend),
with AI consultations powered by **Google Gemini**.

## Features (mapped to scenarios)

| Scenario | What it does | Where |
|---|---|---|
| 1. Onboarding & Initial Assessment | Register, submit financial data, DTI auto-calculated & persisted | `POST /auth/register`, `POST /credit/profile`, `Onboarding.jsx` |
| 2. AI-Powered Financial Consultation | Sends metrics to Gemini, returns analysis + 5-step plan tailored to Indian banking | `POST /advisor/consult`, `services/gemini_service.py`, `AdvisorPanel.jsx` |
| 3. Progress Tracking via Data Viz | Line chart of credit score history over time | `GET /credit/dashboard`, `ScoreChart.jsx` |
| 4. Real-time Credit Health Monitoring | Recalculates score history + deltas + utilization pie chart on every update | `crud.upsert_credit_profile`, `UtilizationChart.jsx` |

## Project Structure

```
credit-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, CORS, router registration
│   │   ├── config.py          # Settings (env vars)
│   │   ├── database.py        # SQLAlchemy engine/session
│   │   ├── models.py          # User, CreditProfile, CreditScoreHistory, AdvisorSession
│   │   ├── schemas.py         # Pydantic request/response models
│   │   ├── auth.py            # Password hashing + JWT
│   │   ├── crud.py            # DB read/write helpers
│   │   ├── routers/
│   │   │   ├── auth.py        # /auth/register, /auth/login
│   │   │   ├── credit.py      # /credit/profile, /credit/dashboard
│   │   │   └── advisor.py     # /advisor/consult
│   │   └── services/
│   │       ├── credit_calc.py     # DTI / utilization / band math
│   │       └── gemini_service.py  # Gemini prompt + fallback logic
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.jsx             # Router + auth state
    │   ├── api/client.js       # Axios client, JWT header injection
    │   ├── pages/
    │   │   ├── Login.jsx / Register.jsx
    │   │   ├── Onboarding.jsx  # financial data form
    │   │   └── Dashboard.jsx   # assembles all widgets
    │   └── components/
    │       ├── ScoreChart.jsx        # line chart (recharts)
    │       ├── UtilizationChart.jsx  # pie chart (recharts)
    │       └── AdvisorPanel.jsx      # triggers AI consult
    ├── index.html
    ├── vite.config.js
    └── package.json
```

## Getting Started

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: set SECRET_KEY and GEMINI_API_KEY
# (Get a Gemini key at https://aistudio.google.com/apikey)

uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. Interactive docs: `http://localhost:8000/docs`.

> Note: If `GEMINI_API_KEY` is left blank, `/advisor/consult` still works using a
> deterministic rule-based fallback, so the app is fully testable without a live key.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs at `http://localhost:5173` and proxies `/auth`, `/credit`, `/advisor` to the backend.

### 3. Try it end-to-end

1. Register a user → log in.
2. You'll be routed to "Enter my financial data" — submit a score, income, expenses, debt, credit limit/used.
3. View your dashboard: current score/band, DTI, utilization pie chart.
4. Click **Get AI Advice** to trigger the Gemini-powered consultation.
5. Update your profile again later (e.g. after paying off debt) — the dashboard will show
   score/utilization deltas and a growing trend line.

## Database

Defaults to SQLite (`credit_assistant.db`) for zero-setup local dev. To use Postgres,
set `DATABASE_URL=postgresql://user:password@host:5432/dbname` in `.env` and
`pip install psycopg2-binary`.

Tables are auto-created on startup via `Base.metadata.create_all`. For schema changes
in a real deployment, switch to Alembic migrations (already in `requirements.txt`).

## Credit Score Bands (CIBIL-style, used for India)

| Score | Band |
|---|---|
| 300–579 | Poor |
| 580–669 | Fair |
| 670–739 | Good |
| 740–799 | Very Good |
| 800–900 | Excellent |

## Security Notes for Production

- Set a strong random `SECRET_KEY`.
- Put the app behind HTTPS; the JWT bearer token is sent in the `Authorization` header.
- Restrict `FRONTEND_ORIGIN` / CORS to your real deployed domain.
- Add rate limiting on `/auth/login` and `/advisor/consult` (Gemini calls cost money).
- Consider hashing/encryption-at-rest policies for financial data depending on your compliance needs.
