"""Database layer (SQLAlchemy 2.0). SQLite by default, PostgreSQL via DATABASE_URL."""
from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy import inspect, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    role: Mapped[str] = mapped_column(String(20), default="student")
    classroom_code: Mapped[str | None] = mapped_column(String(12), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course: Mapped[str] = mapped_column(String(16), default="quantum", index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    lesson_id: Mapped[str] = mapped_column(String(64))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class QuizResult(Base):
    __tablename__ = "quiz_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course: Mapped[str] = mapped_column(String(16), default="quantum", index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    lesson_id: Mapped[str] = mapped_column(String(64))
    topic: Mapped[str] = mapped_column(String(32))
    score: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)
    percent: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ChallengeAttempt(Base):
    __tablename__ = "challenge_attempts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course: Mapped[str] = mapped_column(String(16), default="quantum", index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    challenge_id: Mapped[str] = mapped_column(String(64))
    topic: Mapped[str] = mapped_column(String(32))
    solved: Mapped[bool] = mapped_column(Boolean, default=False)
    fidelity: Mapped[float] = mapped_column(Float, default=0.0)
    points: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Experiment(Base):
    """One simulation run — the learner's experiment history."""

    __tablename__ = "experiments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course: Mapped[str] = mapped_column(String(16), default="quantum", index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    num_qubits: Mapped[int] = mapped_column(Integer, default=0)
    gate_count: Mapped[int] = mapped_column(Integer, default=0)
    depth: Mapped[int] = mapped_column(Integer, default=0)
    backend: Mapped[str] = mapped_column(String(32))
    lab: Mapped[str] = mapped_column(String(32), default="builder")
    state_name: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class SavedCircuit(Base):
    __tablename__ = "saved_circuits"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    num_qubits: Mapped[int] = mapped_column(Integer)
    operations: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class TutorMessage(Base):
    __tablename__ = "tutor_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    question: Mapped[str] = mapped_column(Text)
    provider: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Classroom(Base):
    __tablename__ = "classrooms"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    instructor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Assignment(Base):
    __tablename__ = "assignments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course: Mapped[str] = mapped_column(String(16), default="quantum", index=True)
    classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    item_type: Mapped[str] = mapped_column(String(16))
    item_id: Mapped[str] = mapped_column(String(64))
    due: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Material(Base):
    """A study resource an instructor shares with a classroom (notes and/or a link)."""

    __tablename__ = "materials"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str] = mapped_column(Text, default="")
    link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    course: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ReviewCard(Base):
    """Spaced-repetition state of one flashcard for one learner (SM-2)."""

    __tablename__ = "review_cards"
    __table_args__ = (UniqueConstraint("user_id", "card_id"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    card_id: Mapped[str] = mapped_column(String(96))
    course: Mapped[str] = mapped_column(String(16), index=True)
    ease: Mapped[float] = mapped_column(Float, default=2.5)
    interval: Mapped[float] = mapped_column(Float, default=0.0)
    reps: Mapped[int] = mapped_column(Integer, default=0)
    lapses: Mapped[int] = mapped_column(Integer, default=0)
    due: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ReviewLog(Base):
    __tablename__ = "review_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    card_id: Mapped[str] = mapped_column(String(96))
    course: Mapped[str] = mapped_column(String(16))
    grade: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class FocusSession(Base):
    __tablename__ = "focus_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course: Mapped[str | None] = mapped_column(String(16), nullable=True)
    minutes: Mapped[int] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(String(120), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Note(Base):
    __tablename__ = "notes"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course: Mapped[str] = mapped_column(String(16))
    lesson_id: Mapped[str] = mapped_column(String(64))
    text: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


# ===========================================================================
# Finale additions (v2.4) — community chat, leaderboards, course authoring,
# instructor tests, end-of-course mini-projects, LeetCode practice, institutions.
# All additive: new tables only, created automatically by create_all().
# ===========================================================================
class ChatMessage(Base):
    """A message in a classroom's community discussion."""

    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    classroom_code: Mapped[str] = mapped_column(String(12), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(80))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


class AuthoredCourse(Base):
    """A course an instructor builds on the platform (with video lessons)."""

    __tablename__ = "authored_courses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(48), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(160))
    summary: Mapped[str] = mapped_column(Text, default="")
    instructor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    instructor_name: Mapped[str] = mapped_column(String(80), default="")
    price: Mapped[int] = mapped_column(Integer, default=0)   # 0 = free (paid tier is a separate add-on)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AuthoredLesson(Base):
    __tablename__ = "authored_lessons"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("authored_courses.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    video_url: Mapped[str | None] = mapped_column(String(600), nullable=True)
    body: Mapped[str] = mapped_column(Text, default="")
    order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Test(Base):
    """An instructor-authored test / quiz."""

    __tablename__ = "tests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    course: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)
    instructor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    classroom_code: Mapped[str | None] = mapped_column(String(12), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class TestQuestion(Base):
    __tablename__ = "test_questions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id", ondelete="CASCADE"), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    options: Mapped[list] = mapped_column(JSON)
    answer: Mapped[int] = mapped_column(Integer, default=0)
    explain: Mapped[str] = mapped_column(Text, default="")
    order: Mapped[int] = mapped_column(Integer, default=0)


class TestResult(Base):
    __tablename__ = "test_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(80))
    score: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ProjectSubmission(Base):
    """A learner's submission for an end-of-course mini-project."""

    __tablename__ = "project_submissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64), index=True)
    course: Mapped[str] = mapped_column(String(16), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    link: Mapped[str | None] = mapped_column(String(600), nullable=True)
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class PracticeSolved(Base):
    """Marks a linked LeetCode-style practice problem as solved by a learner."""

    __tablename__ = "practice_solved"
    __table_args__ = (UniqueConstraint("user_id", "slug"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course: Mapped[str] = mapped_column(String(16), index=True)
    slug: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Institution(Base):
    """An organisation that signs its members in through institution (SSO) mode."""

    __tablename__ = "institutions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    domain: Mapped[str | None] = mapped_column(String(120), nullable=True)
    admin_name: Mapped[str] = mapped_column(String(80), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class InstitutionMember(Base):
    __tablename__ = "institution_members"
    __table_args__ = (UniqueConstraint("institution_id", "email"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(160))
    role: Mapped[str] = mapped_column(String(20), default="student")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


_engine = None
_SessionLocal: sessionmaker | None = None


def init_db(url: str) -> None:
    """Create the engine and tables. Called on app start-up (and by tests)."""
    global _engine, _SessionLocal
    kwargs: dict = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        if url in ("sqlite://", "sqlite:///:memory:"):
            from sqlalchemy.pool import StaticPool

            kwargs["poolclass"] = StaticPool
    _engine = create_engine(url, **kwargs)
    _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
    Base.metadata.create_all(_engine)
    _migrate(_engine)


def _migrate(engine) -> None:
    """Add columns introduced after v1.0 to existing databases (simple, additive only)."""
    wanted = {
        "lesson_progress": [("course", "VARCHAR(16) DEFAULT 'quantum'")],
        "quiz_results": [("course", "VARCHAR(16) DEFAULT 'quantum'")],
        "challenge_attempts": [("course", "VARCHAR(16) DEFAULT 'quantum'")],
        "experiments": [("course", "VARCHAR(16) DEFAULT 'quantum'"), ("lab", "VARCHAR(32) DEFAULT 'builder'")],
        "assignments": [("course", "VARCHAR(16) DEFAULT 'quantum'")],
    }
    insp = inspect(engine)
    with engine.begin() as conn:
        for table, cols in wanted.items():
            if not insp.has_table(table):
                continue
            have = {c["name"] for c in insp.get_columns(table)}
            for name, ddl in cols:
                if name not in have:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))


def get_session() -> Iterator[Session]:
    if _SessionLocal is None:
        raise RuntimeError("Database not initialised — call init_db() first")
    with _SessionLocal() as session:
        yield session
