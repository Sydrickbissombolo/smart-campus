# Smart Campus IT – Service Portal (PostgreSQL Edition)

Portal with: Login, Submit Ticket, View/Update Ticket, **Comments**, **Attachments**, **Assignments**, Email notifications, CLI tools.

## Quick Start (Dev)
1) **Python & deps**
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r backend/requirements.txt
```

2) **Environment**
```bash
cp backend/.env.example backend/.env
# Edit DATABASE_URL to our PostgreSQL instance
# Example: postgresql://postgres:postgres@localhost:5432/smartcampus
```

3) **Run DB seed & API**
```bash
python backend/seed.py
python backend/app.py
```

4) **Serve frontend**
- Using VS Code Live Server

cd frontend
python -m http.server 5500
# open http://127.0.0.1:5500/login.html
```

## Demo Accounts
- Student: `newton@student.test` / `newton123`
- Faculty: `charmant@faculty.test` / `charmant123`
- Tech: `glorion@it.test` / `glorion123`
- Admin: `bissombolo@it.test` / `bissombolo123`

## Included Features
- **Comments**: add and list comments per ticket
- **Attachments**: upload/download files (png, jpg, jpeg, gif, pdf, txt, log, zip)
- **Assignments**: assign tickets to TECH/ADMIN users

## API Highlights
- `POST /api/tickets/:id/comments`
- `GET /api/tickets/:id/comments`
- `POST /api/tickets/:id/attachments` (multipart/form-data with `file`)
- `GET /api/attachments/:id/download`
- `POST /api/tickets/:id/assign`
- `GET /api/users?role=TECH|ADMIN`

