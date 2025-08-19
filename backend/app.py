import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from db import Base, engine, SessionLocal
from models import User, Ticket, TicketStatus, Role, Comment, Attachment
from auth import hash_password, verify_password, create_token, decode_token
from config import Config
from mailer import send_email
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH_MB * 1024 * 1024
CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

# init DB
Base.metadata.create_all(bind=engine)

# ensure upload dir exists (relative to backend folder)
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), Config.UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ----- Helpers -----
def require_auth(roles: list[str] | None = None):
    def wrapper(func):
        def inner(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing or invalid token"}), 401
            token = auth_header.split(" ", 1)[1]
            try:
                payload = decode_token(token)
                request.user = payload
                if roles and payload.get("role") not in roles:
                    return jsonify({"error": "Forbidden"}), 403
            except Exception as e:
                return jsonify({"error": "Unauthorized", "detail": str(e)}), 401
            return func(*args, **kwargs)
        inner.__name__ = func.__name__
        return inner
    return wrapper

def serialize_ticket(t: Ticket):
    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "status": t.status.value,
        "creator_id": t.creator_id,
        "assignee_id": t.assignee_id,
        "created_at": t.created_at.isoformat(),
        "updated_at": t.updated_at.isoformat(),
    }

def serialize_user(u: User):
    return {"id": u.id, "name": u.name, "email": u.email, "role": u.role.value}

def serialize_comment(c: Comment):
    return {
        "id": c.id,
        "ticket_id": c.ticket_id,
        "user_id": c.user_id,
        "content": c.content,
        "created_at": c.created_at.isoformat(),
        "user": serialize_user(c.user) if c.user else None
    }

def serialize_attachment(a: Attachment):
    return {
        "id": a.id,
        "ticket_id": a.ticket_id,
        "filename": a.filename,
        "path": f"/api/attachments/{a.id}/download",
        "uploaded_at": a.uploaded_at.isoformat(),
    }

# ----- Auth -----
@app.post('/api/auth/register')
def register():
    data = request.json or {}
    email = data.get('email', '').lower().strip()
    name = data.get('name', '').strip()
    password = data.get('password', '')
    role = data.get('role', Role.STUDENT.value)

    if not email or not password or not name:
        return jsonify({"error": "Missing fields"}), 400

    with SessionLocal() as db:
        user = User(email=email, name=name, password_hash=hash_password(password), role=Role(role))
        db.add(user)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return jsonify({"error": "Email already registered"}), 409
        return jsonify({"id": user.id, "email": user.email, "role": user.role.value})

@app.post('/api/auth/login')
def login():
    data = request.json or {}
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"error": "Invalid credentials"}), 401
        token = create_token(user.id, user.role.value, user.email)
        return jsonify({"token": token, "user": serialize_user(user)})

# ----- Users -----
@app.get('/api/users')
@require_auth(roles=[Role.ADMIN.value, Role.TECH.value])
def list_users():
    role = request.args.get("role")
    with SessionLocal() as db:
        q = select(User)
        if role:
            q = q.where(User.role == Role(role))
        users = db.scalars(q).all()
        return jsonify([serialize_user(u) for u in users])

# ----- Tickets CRUD -----
@app.post('/api/tickets')
@require_auth()
def create_ticket():
    data = request.json or {}
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    if not title or not description:
        return jsonify({"error": "Title and description are required"}), 400

    with SessionLocal() as db:
        user = db.get(User, int(request.user['sub']))
        ticket = Ticket(title=title, description=description, creator=user)
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        try:
            send_email(user.email, "Ticket received", f"Hello {user.name}, your ticket #{ticket.id} was created and is OPEN.")
        except Exception:
            pass

        return jsonify(serialize_ticket(ticket))

@app.get('/api/tickets')
@require_auth()
def list_tickets():
    status = request.args.get('status')
    my = request.args.get('my') == '1'
    with SessionLocal() as db:
        q = select(Ticket)
        if status:
            q = q.where(Ticket.status == TicketStatus(status))
        if my:
            q = q.where(Ticket.creator_id == int(request.user['sub']))
        tickets = db.scalars(q).all()
        return jsonify([serialize_ticket(t) for t in tickets])

@app.get('/api/tickets/<int:ticket_id>')
@require_auth()
def get_ticket(ticket_id: int):
    with SessionLocal() as db:
        t = db.get(Ticket, ticket_id)
        if not t:
            return jsonify({"error": "Not found"}), 404
        data = serialize_ticket(t)
        data["comments"] = [serialize_comment(c) for c in t.comments]
        data["attachments"] = [serialize_attachment(a) for a in t.attachments]
        return jsonify(data)

@app.patch('/api/tickets/<int:ticket_id>')
@require_auth(roles=[Role.TECH.value, Role.ADMIN.value])
def update_ticket(ticket_id: int):
    data = request.json or {}
    with SessionLocal() as db:
        t = db.get(Ticket, ticket_id)
        if not t:
            return jsonify({"error": "Not found"}), 404
        if 'status' in data:
            t.status = TicketStatus(data['status'])
        if 'assignee_id' in data:
            t.assignee_id = data['assignee_id']
        db.commit()
        db.refresh(t)

        if t.status == TicketStatus.RESOLVED:
            try:
                creator = db.get(User, t.creator_id)
                send_email(creator.email, "Ticket resolved", f"Hello {creator.name}, your ticket #{t.id} has been RESOLVED.")
            except Exception:
                pass

        return jsonify(serialize_ticket(t))

# ----- Assignment -----
@app.post('/api/tickets/<int:ticket_id>/assign')
@require_auth(roles=[Role.TECH.value, Role.ADMIN.value])
def assign_ticket(ticket_id: int):
    data = request.json or {}
    assignee_id = data.get("assignee_id")
    if not assignee_id:
        return jsonify({"error": "assignee_id required"}), 400
    with SessionLocal() as db:
        t = db.get(Ticket, ticket_id)
        if not t:
            return jsonify({"error": "Not found"}), 404
        t.assignee_id = assignee_id
        db.commit()
        db.refresh(t)
        return jsonify(serialize_ticket(t))

# ----- Comments -----
@app.get('/api/tickets/<int:ticket_id>/comments')
@require_auth()
def list_comments(ticket_id: int):
    with SessionLocal() as db:
        t = db.get(Ticket, ticket_id)
        if not t:
            return jsonify({"error": "Not found"}), 404
        return jsonify([serialize_comment(c) for c in t.comments])

@app.post('/api/tickets/<int:ticket_id>/comments')
@require_auth()
def add_comment(ticket_id: int):
    data = request.json or {}
    content = data.get("content", "").strip()
    if not content:
        return jsonify({"error": "content required"}), 400
    with SessionLocal() as db:
        t = db.get(Ticket, ticket_id)
        if not t:
            return jsonify({"error": "Not found"}), 404
        user_id = int(request.user["sub"])
        c = Comment(ticket_id=t.id, user_id=user_id, content=content)
        db.add(c)
        db.commit()
        db.refresh(c)
        return jsonify(serialize_comment(c)), 201

# ----- Attachments -----
ALLOWED_EXT = {"png","jpg","jpeg","gif","pdf","txt","log","zip"}

@app.post('/api/tickets/<int:ticket_id>/attachments')
@require_auth()
def upload_attachment(ticket_id: int):
    with SessionLocal() as db:
        t = db.get(Ticket, ticket_id)
        if not t:
            return jsonify({"error": "Not found"}), 404

    if 'file' not in request.files:
        return jsonify({"error": "file field required"}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({"error": "empty filename"}), 400
    ext = f.filename.rsplit('.',1)[-1].lower() if '.' in f.filename else ''
    if ext not in ALLOWED_EXT:
        return jsonify({"error": f"extension .{ext} not allowed"}), 400

    safe = secure_filename(f.filename)
    save_path = os.path.join(UPLOAD_DIR, safe)
    f.save(save_path)

    with SessionLocal() as db:
        a = Attachment(ticket_id=ticket_id, filename=safe, path=save_path)
        db.add(a)
        db.commit()
        db.refresh(a)
        return jsonify(serialize_attachment(a)), 201

@app.get('/api/attachments/<int:attachment_id>/download')
@require_auth()
def download_attachment(attachment_id: int):
    with SessionLocal() as db:
        a = db.get(Attachment, attachment_id)
        if not a:
            return jsonify({"error": "Not found"}), 404
    directory = os.path.dirname(a.path)
    filename = os.path.basename(a.path)
    return send_from_directory(directory, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=(Config.FLASK_ENV == 'development'))
