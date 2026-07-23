# BIM Project — Backend + Frontend

## backend/  (FastAPI, unchanged)
cd backend
pip install -r requirements.txt   # or install: fastapi, uvicorn, sqlalchemy, aiosqlite, pydantic-settings
uvicorn app.main:app --reload --port 8000

## frontend/ (Next.js 16, TypeScript, Tailwind v4)
cd frontend
npm install
npm run dev
# open http://localhost:3000
# API base URL is set in frontend/.env.local -> NEXT_PUBLIC_API_URL

Frontend consumes exactly the endpoints exposed by the backend:
buildings, floors (+ /buildings/{id}/floors), rooms (+ /floors/{id}/rooms),
structural-elements (+ /rooms/{id}/elements). No upload/search endpoints exist
on the backend, so those pages were intentionally omitted per your instruction.
