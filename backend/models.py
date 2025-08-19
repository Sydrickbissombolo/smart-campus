from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base
import enum

class Role(str, enum.Enum):
    STUDENT = "STUDENT"
    FACULTY = "FACULTY"
    TECH = "TECH"
    ADMIN = "ADMIN"

class TicketStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.STUDENT)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="creator", foreign_keys="Ticket.creator_id")
    assigned_tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="assignee", foreign_keys="Ticket.assignee_id")

class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(4000))
    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus), default=TicketStatus.OPEN)

    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    creator: Mapped[User] = relationship("User", back_populates="tickets", foreign_keys=[creator_id])

    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    assignee: Mapped[User | None] = relationship("User", back_populates="assigned_tickets", foreign_keys=[assignee_id])

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="ticket", cascade="all, delete-orphan")
    attachments: Mapped[list["Attachment"]] = relationship("Attachment", back_populates="ticket", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ticket: Mapped[Ticket] = relationship("Ticket", back_populates="comments")
    user: Mapped[User] = relationship("User")

class Attachment(Base):
    __tablename__ = "attachments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    filename: Mapped[str] = mapped_column(String(512))
    path: Mapped[str] = mapped_column(String(1024))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ticket: Mapped[Ticket] = relationship("Ticket", back_populates="attachments")
