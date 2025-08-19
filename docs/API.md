# API Reference (PostgreSQL Edition)

Base URL: `http://127.0.0.1:5000`

## Auth
### POST /api/auth/register
Body: `{ email, name, password, role }`

### POST /api/auth/login
Body: `{ email, password }`
Response: `{ token, user }`

Header for protected routes: `Authorization: Bearer <token>`

## Users
### GET /api/users?role=TECH|ADMIN
List users by role. (TECH/ADMIN only)

## Tickets
### POST /api/tickets
Body: `{ title, description }`

### GET /api/tickets?status=OPEN|IN_PROGRESS|RESOLVED&my=1
Response: `[{...ticket}]`

### GET /api/tickets/:id
Includes `comments` and `attachments` arrays.

### PATCH /api/tickets/:id
Body: `{ status, assignee_id }` (TECH/ADMIN only)

### POST /api/tickets/:id/assign
Body: `{ assignee_id }` (TECH/ADMIN only)

## Comments
### GET /api/tickets/:id/comments
### POST /api/tickets/:id/comments
Body: `{ content }`

## Attachments
### POST /api/tickets/:id/attachments
multipart form-data with field `file`
Allowed: png, jpg, jpeg, gif, pdf, txt, log, zip

### GET /api/attachments/:id/download
