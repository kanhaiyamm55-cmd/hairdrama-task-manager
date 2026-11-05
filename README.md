# Hairdrama Task Manager

A full-stack task management application built with Next.js, TypeScript, Flask, Supabase and Google OAuth.

## Features
- Google authentication using Supabase Auth
- Create and manage tasks
- Assign tasks to registered users
- Update task status: Pending, In Progress and Completed
- Supabase database integration
- Gmail notifications for task assignment and completion
- Responsive dashboard

## Tech Stack
- Frontend: Next.js, React, TypeScript
- Backend: Python, Flask
- Database: Supabase PostgreSQL
- Authentication: Google OAuth 2.0 with Supabase
- Email: Gmail SMTP
- Deployment: Vercel and Render

## Project Structure
- `frontend/` – Next.js application
- `backend/` – Flask API
- `backend/migrations/` – Database migration SQL

## Local Setup

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
python run.py
```

## Environment Variables

Configure the required variables using the `.env.example` files.

Frontend:
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `NEXT_PUBLIC_API_BASE_URL`

Backend:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `FRONTEND_ORIGIN`
- `GMAIL_SENDER`
- `GMAIL_APP_PASSWORD`

Never commit actual credentials or secret keys.

## Live Application
Frontend: https://frontend-khaki-psi-48.vercel.app/

Backend: https://hairdrama-task-manager-api-c2is.onrender.com/

## Developer
Developed as a full-stack task management assignment.
