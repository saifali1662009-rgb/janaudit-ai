# Deploy and test Janaudit AI

## 1. Put your Mesh key in the backend only

In the `backend` folder, make a copy of `.env.example` named `.env`.

Paste the key after `MESH_API_KEY=`:

```env
MESH_API_KEY=rsk_paste_your_actual_key_here
```

Do not paste the key into `app/page.tsx`, `.env.local`, GitHub, Vercel, or any browser form.

## 2. Run it on your computer

Install Node.js LTS and Python 3.11+ first. Then open two terminals.

Backend terminal:

```powershell
cd F:\Janaudit-AI\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Frontend terminal:

```powershell
cd F:\Janaudit-AI
copy .env.local.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`. Open `http://localhost:8000/health` to check the backend.

## 3. Deploy the backend to Render

1. Push this repository to GitHub. Do not include either `.env` file.
2. In Render, choose **New +** → **Blueprint** and select the repository.
3. Render finds `backend/render.yaml`.
4. Add the `MESH_API_KEY` value in the secret environment-variable field.
5. Set `FRONTEND_ORIGIN` after Vercel gives you the frontend URL.
6. Deploy and copy the public backend URL, for example `https://janaudit-api.onrender.com`.

## 4. Deploy the frontend to Vercel

1. In Vercel, choose **Add New** → **Project**, then select the same GitHub repository.
2. Set the Root Directory to the repository root (`.`).
3. Add an environment variable:

```env
NEXT_PUBLIC_API_URL=https://janaudit-api.onrender.com
```

4. Deploy. Copy the Vercel URL and add it as `FRONTEND_ORIGIN` in Render.
5. Redeploy the Render service.

## Test checklist

- Visit `/health`: it should return `{"status":"ok","mesh":"configured"}`.
- Open the Vercel site and use Investigation Mode.
- Confirm that returned source links are government, CAG, PIB, or Parliament pages.
- Confirm the browser developer tools never show `MESH_API_KEY`.
- Check the Mesh Logs page after one test to verify the request reached Mesh.

> Current note: the next code update switches Mesh use from text generation to `vertex/text-embedding-005` for evidence ranking. Do not deploy until that update has been applied.
