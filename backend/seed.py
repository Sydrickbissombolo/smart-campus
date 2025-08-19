from db import Base, engine, SessionLocal
from models import User, Role, Ticket, TicketStatus
from auth import hash_password

def seed():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.query(User).count():
            users = [
                User(name="Newton Student", email="newton@student.test", role=Role.STUDENT, password_hash=hash_password("newton123")),
                User(name="Charmant Faculty", email="charmant@faculty.test", role=Role.FACULTY, password_hash=hash_password("charmant123")),
                User(name="Glorion Tech", email="glorion@it.test", role=Role.TECH, password_hash=hash_password("glorion123")),
                User(name="Bissombolo Admin", email="bissombolo@it.test", role=Role.ADMIN, password_hash=hash_password("bissombolo123")),
            ]
            db.add_all(users)
            db.commit()
        if not db.query(Ticket).count():
            student = db.query(User).filter_by(email="newton@student.test").first()
            t = Ticket(title="Can't connect to campus Wi-Fi", description="Wifi times out", creator_id=student.id, status=TicketStatus.OPEN)
            db.add(t)
            db.commit()

if __name__ == "__main__":
    seed()
    print("Seed complete.")
