# Architecture & Flows

## Components
- **Frontend**: Static pages, calls Flask API via Fetch.
- **Backend**: Flask API + SQLAlchemy + JWT.
- **DB**: PostgreSQL (via `psycopg2-binary`).
- **Email**: SMTP (debug or real relay).
- **CLI**: Shared DB access for Help Desk.

## Ticket Flow
1. User logs in → gets JWT.
2. User submits ticket → API stores ticket → sends email "Ticket received".
3. Tech/Admin assigns ticket → updates status → API sends email on RESOLVED.
4. Comments and attachments enrich the ticket.

## Security Notes
- Hash passwords (bcrypt via passlib).
- JWT secret from ENV, rotate for prod.
- Limit CORS to known origins in prod.
- Validate file types and size limits on uploads.
