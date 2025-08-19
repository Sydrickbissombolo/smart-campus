#!/usr/bin/env python
"""Smart Campus CLI for Help Desk & Reporting
Usage:
  python scripts/cli.py users add --name "Theresia Tech" --email theresia@it.test --role TECH --password 123456
  python scripts/cli.py tickets list [--status OPEN|IN_PROGRESS|RESOLVED] [--email newton@student.test]
  python scripts/cli.py tickets update --id 1 --status RESOLVED
"""

import argparse
from sqlalchemy import select
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1] / 'backend'))

from db import SessionLocal
from models import User, Role, Ticket, TicketStatus
from auth import hash_password

def add_user(args):
    with SessionLocal() as db:
        user = User(name=args.name, email=args.email.lower(), role=Role(args.role), password_hash=hash_password(args.password))
        db.add(user)
        db.commit()
        print(f"Created user {user.id} {user.email} ({user.role.value})")

def list_tickets(args):
    with SessionLocal() as db:
        q = select(Ticket)
        if args.status:
            q = q.where(Ticket.status == TicketStatus(args.status))
        if args.email:
            user = db.scalars(select(User).where(User.email == args.email.lower())).first()
            if user:
                q = q.where(Ticket.creator_id == user.id)
        rows = db.scalars(q).all()
        for t in rows:
            print(f"#{t.id} {t.title} [{t.status.value}] by user {t.creator_id} -> assignee {t.assignee_id}")

def update_ticket(args):
    with SessionLocal() as db:
        t = db.get(Ticket, args.id)
        if not t:
            print("Ticket not found")
            return
        t.status = TicketStatus(args.status)
        db.commit()
        print(f"Ticket #{t.id} set to {t.status.value}")

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd')

    pu = sub.add_parser('users')
    su = pu.add_subparsers(dest='ucmd')
    addp = su.add_parser('add')
    addp.add_argument('--name', required=True)
    addp.add_argument('--email', required=True)
    addp.add_argument('--role', required=True, choices=[r.value for r in Role])
    addp.add_argument('--password', required=True)
    addp.set_defaults(func=add_user)

    pt = sub.add_parser('tickets')
    st = pt.add_subparsers(dest='tcmd')
    listp = st.add_parser('list')
    listp.add_argument('--status', choices=[s.value for s in TicketStatus])
    listp.add_argument('--email')
    listp.set_defaults(func=list_tickets)

    upd = st.add_parser('update')
    upd.add_argument('--id', type=int, required=True)
    upd.add_argument('--status', required=True, choices=[s.value for s in TicketStatus])
    upd.set_defaults(func=update_ticket)

    args = p.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        p.print_help()

if __name__ == '__main__':
    main()
