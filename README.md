# Janaudit AI

**Understand public spending. Backed by evidence.**

Janaudit AI is a public-finance transparency project for the Mesh API Hackathon. It helps citizens explore government schemes, budgets and projects through source-backed explanations, not political opinions.

## Stack

- Frontend: Next.js / React
- Backend: FastAPI
- AI: [Mesh API](https://developers.meshapi.ai/docs/guides/quickstart) using its OpenAI-compatible chat-completions endpoint
- Sources: accessible Government of India, CAG, PIB and Parliament pages

## Run locally

### Frontend

```powershell
npm install
npm run dev
```

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Set `MESH_API_KEY` in `backend/.env`. Do not commit that file or expose this key to the browser.

## API

- `GET /health` checks service and Mesh configuration.
- `POST /api/investigations` handles structured Investigation Mode input.
- `POST /api/search` handles a natural-language question.

The backend retrieves a small group of authoritative pages first, extracts relevant text, and sends only that evidence to Mesh. It refuses to create a report when sources or Mesh are unavailable, avoiding fabricated information.
