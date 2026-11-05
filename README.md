# Task Manager — Hairdrama Tech Assignment Starter

This is a **learning starter**, not a finished submission. It gives you a runnable Next.js + TypeScript frontend and Flask API skeleton, plus a Supabase migration template. Complete the TODOs yourself and be ready to explain every line.

## Stack
- Frontend: Next.js App Router + TypeScript
- Backend: Flask
- Database/Auth: Supabase (PostgreSQL + Supabase Auth / Google OAuth)
- Email: Gmail API or SMTP with OAuth (implement after core task flows)

## Requirements
- Node.js 20+
- Python 3.10+
- Git
- Supabase project

## 1. Run the backend
```bash
cd backend
python -m venv venv
# Windows CMD:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```
Backend health check: http://127.0.0.1:5000/api/health

## 2. Run the frontend
Open a second terminal:
```bash
cd frontend
npm install
copy .env.example .env.local
npm run dev
```
Open http://localhost:3000

## 3. Supabase setup
1. Create a Supabase project.
2. Open SQL Editor and run `backend/migrations/001_initial_schema.sql`.
3. Copy Project URL and anon key into `frontend/.env.local`.
4. Copy Project URL and service role key into `backend/.env` (server only; never expose it in frontend).
5. Enable Google provider in Supabase Auth and configure the OAuth redirect URLs shown by Supabase.

## Important security notes
- Never commit `.env`, `.env.local`, OAuth client secrets, Gmail credentials, or Supabase service-role keys.
- Frontend uses only the Supabase anon/publishable key.
- Backend must verify the Supabase access token on every protected route.
- Add and test RLS policies before using real user data.
- Do not claim Gmail notifications or task assignment are complete until implemented and tested.

## Suggested implementation order
1. Supabase Google OAuth sign-in/sign-out.
2. Backend JWT verification middleware.
3. Task CRUD with ownership checks.
4. User search and task assignment.
5. Email notification on task creation/completion.
6. RLS tests, API tests, deployment, README architecture diagram, Loom walkthrough.

## API starter endpoints
- `GET /api/health` — implemented.
- `GET /api/tasks` — TODO: authenticated list.
- `POST /api/tasks` — TODO: create.
- `PATCH /api/tasks/<task_id>` — TODO: update status/details.
- `POST /api/tasks/<task_id>/assign` — TODO: assign user.

## Architecture
Browser (Next.js) -> Flask REST API -> Supabase PostgreSQL.
Browser signs in using Supabase Auth (Google OAuth) and sends the access token to Flask.
Flask verifies the token and performs authorization before reading/writing data.
Email service is called by Flask after successful task creation or completion.
