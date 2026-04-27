**Backend**
Render service settings:

- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

Required Render environment variables:

- `ENV=production`
- `DEBUG=false`
- `DATABASE_URL=<neon postgres url with sslmode=require>`
- `JWT_SECRET=<32+ random chars>`
- `ADMIN_EMAIL=<admin email>`
- `ADMIN_PASSWORD=<temporary admin password>`
- `RUN_DB_INIT=false`
- `ALLOWED_ORIGINS=["https://mamh.vercel.app"]`

One-time DB init:

1. Temporarily set `RUN_DB_INIT=true`
2. Let Render redeploy, or run manually in the Render shell:

```bash
cd ~/project/src/backend
python -c "from app.db.init_db import init_db; init_db()"
```

3. Set `RUN_DB_INIT=false`

Health check:

- `GET /health`

**Frontend**
Vercel project settings:

- Root Directory: `frontend/react-frontend`

Required Vercel environment variable:

- `VITE_API_BASE_URL=https://mamh.onrender.com/api/v1`

Notes:

- The frontend now only falls back to `http://localhost:8000/api/v1` when running on `localhost`.
- Production builds require `VITE_API_BASE_URL` explicitly.
- The Godot iframe receives the same API base URL through the React Play page.
