"""Pydantic request/response models shared by the API routers."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Operation(BaseModel):
    """One gate application. ``qubits`` is ``[controls..., target]`` for controlled gates."""

    name: str = Field(..., examples=["h"])
    qubits: list[int] = Field(..., examples=[[0]])
    params: list[float] = Field(default_factory=list)
    col: int | None = Field(None, description="Column in the visual builder (optional, for UI sync)")


class Circuit(BaseModel):
    num_qubits: int = Field(2, ge=1, le=10)
    operations: list[Operation] = Field(default_factory=list)


class SimulateRequest(Circuit):
    shots: int = Field(1024, ge=1, le=8192)
    backend: Literal["auto", "q3d", "qiskit"] = "auto"
    include_steps: bool = True
    seed: int | None = None
    user_id: int | None = None


class QasmImportRequest(BaseModel):
    qasm: str


class LabContext(BaseModel):
    """What the learner is looking at in a visual lab (facts computed by the backend engines)."""

    lab: str = Field(..., max_length=40)
    title: str = Field("", max_length=120)
    facts: list[str] = Field(default_factory=list, max_length=30)


class TutorRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    circuit: Circuit | None = None
    result: dict[str, Any] | None = None
    history: list[dict[str, str]] = Field(default_factory=list)
    lesson_id: str | None = None
    challenge_id: str | None = None
    user_id: int | None = None
    course: str | None = None
    lab: LabContext | None = None


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    role: Literal["student", "instructor"] = "student"
    classroom_code: str | None = None


class LessonComplete(BaseModel):
    user_id: int
    lesson_id: str


class QuizSubmit(BaseModel):
    user_id: int | None = None
    answers: list[int]


class ChallengeCheck(Circuit):
    user_id: int | None = None


class SaveCircuit(Circuit):
    user_id: int
    title: str = Field("Untitled circuit", max_length=120)


class ClassroomCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    instructor_id: int


class AssignmentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=160)
    course: str = "quantum"
    item_type: Literal["lesson", "challenge"]
    item_id: str
    due: str | None = None


class MaterialCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=160)
    body: str = Field("", max_length=20000)
    link: str | None = Field(None, max_length=500)
    course: str | None = None
    instructor_id: int


# --------------------------------------------------------------------- finale (v2.4)
class ChatSend(BaseModel):
    user_id: int | None = None
    name: str = Field("Guest", min_length=1, max_length=80)
    body: str = Field(..., min_length=1, max_length=2000)


class AuthoredCourseCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=160)
    summary: str = Field("", max_length=4000)
    instructor_id: int
    price: int = Field(0, ge=0, le=100000)


class AuthoredLessonCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    video_url: str | None = Field(None, max_length=600)
    body: str = Field("", max_length=20000)
    instructor_id: int


class QuestionIn(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    options: list[str] = Field(..., min_length=2, max_length=8)
    answer: int = Field(0, ge=0)
    explain: str = Field("", max_length=2000)


class TestCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    course: str | None = None
    classroom_code: str | None = None
    instructor_id: int
    questions: list[QuestionIn] = Field(default_factory=list, max_length=50)


class TestSubmit(BaseModel):
    user_id: int | None = None
    name: str = Field("Guest", max_length=80)
    answers: list[int]


class ProjectSubmit(BaseModel):
    user_id: int
    name: str = Field("", max_length=80)
    link: str | None = Field(None, max_length=600)
    note: str = Field("", max_length=4000)


class PracticeSolve(BaseModel):
    user_id: int
    course: str
    slug: str = Field(..., max_length=120)
    solved: bool = True


class InstitutionCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=160)
    domain: str | None = Field(None, max_length=120)
    admin_name: str = Field("", max_length=80)


class SsoLogin(BaseModel):
    code: str = Field(..., min_length=3, max_length=16)
    name: str = Field(..., min_length=1, max_length=80)
    email: str = Field(..., min_length=3, max_length=160)
    role: Literal["student", "instructor"] = "student"
