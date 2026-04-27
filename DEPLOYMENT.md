# Deployment Guide

This project should be deployed as two services:

- Backend: Render Web Service from `backend/`
- Frontend: Vercel static Vite app from `Frontend/`

## 1. Backend On Render

Use the root `render.yaml` blueprint, or create a Render Web Service manually.

Manual settings:

- Root Directory: `backend`
- Runtime: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1`
- Health Check Path: `/health`

Backend environment variables:

```env
PYTHON_VERSION=3.11.11
GEMINI_API_KEY=...
GEMINI_MODELS=models/gemini-2.5-flash,models/gemini-2.5-flash-lite,models/gemini-2.0-flash,models/gemini-2.0-flash-lite,models/gemini-pro-latest
GENERATE_VIDEO=false
MAX_VIDEO_SLIDES=4
MAX_SLIDE_SECONDS=8
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
MONGO_URI=...
MONGO_DB_NAME=shikshaflow
JWT_SECRET_KEY=...
FRONTEND_ORIGINS=https://your-vercel-domain.vercel.app
```

Set `JWT_SECRET_KEY` to a long random value of at least 64 characters.

## 2. Frontend On Vercel

Create a Vercel project using:

- Root Directory: `Frontend`
- Framework Preset: Vite
- Build Command: `npm run build`
- Output Directory: `dist`

Frontend environment variables:

```env
VITE_API_BASE_URL=https://your-render-backend.onrender.com
```

After setting or changing Vercel environment variables, redeploy the frontend.

## 3. Atlas Network Access

For MongoDB Atlas, add Render's outbound IP if available on your plan, or temporarily allow:

```txt
0.0.0.0/0
```

Use a strong database password and do not commit `.env`.

## 4. Storage Model

- MongoDB stores users, lecture records, quizzes, and doubt sessions.
- Cloudinary stores generated videos, slide images, PPTX files, and voiceover files.
- `backend/output/` is temporary runtime working storage only and is ignored by git.

## 5. Final Smoke Test

After both services deploy:

1. Open backend `/health`.
2. Set `FRONTEND_ORIGINS` on Render to the final Vercel URL.
3. Set `VITE_API_BASE_URL` on Vercel to the final Render URL.
4. Sign up.
5. Generate lecture assets.
6. Ask a chatbot question.
7. Start a doubt session.
