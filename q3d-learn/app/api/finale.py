"""Finale features (v2.4): community chat, per-course leaderboards, instructor course
authoring, tests, end-of-course mini-projects, LeetCode practice and institution (SSO) mode.

Everything here is additive — new endpoints over new tables, nothing existing is changed.
"""
from __future__ import annotations

import re
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..courses import leetcode, registry as R
from ..courses import projects as P
from ..database import (
    AuthoredCourse,
    AuthoredLesson,
    ChallengeAttempt,
    ChatMessage,
    Classroom,
    Institution,
    InstitutionMember,
    LessonProgress,
    PracticeSolved,
    ProjectSubmission,
    QuizResult,
    Test,
    TestQuestion,
    TestResult,
    User,
    get_session,
)
from ..schemas import (
    AuthoredCourseCreate,
    AuthoredLessonCreate,
    ChatSend,
    InstitutionCreate,
    PracticeSolve,
    ProjectSubmit,
    SsoLogin,
    TestCreate,
    TestSubmit,
)
from ..services.progress import XP_LESSON, XP_PER_CORRECT

router = APIRouter(prefix="/api", tags=["finale"])


def _rand(n: int, alphabet: str = string.ascii_uppercase + string.digits) -> str:
    return "".join(secrets.choice(alphabet) for _ in range(n))


# =============================================================== leaderboards
@router.get("/leaderboard/{course}")
def leaderboard(course: str, limit: int = 50, db: Session = Depends(get_session)) -> dict:
    """Per-course (or 'all') XP leaderboard, built from existing progress tables."""
    valid = set(R.course_ids())
    scope = None if course == "all" else course
    if scope and scope not in valid:
        raise HTTPException(404, f"Unknown course '{course}'")

    lq = select(LessonProgress)
    qq = select(QuizResult)
    cq = select(ChallengeAttempt)
    if scope:
        lq = lq.where(LessonProgress.course == scope)
        qq = qq.where(QuizResult.course == scope)
        cq = cq.where(ChallengeAttempt.course == scope)

    agg: dict[int, dict] = {}

    def row(uid: int) -> dict:
        return agg.setdefault(uid, {"lessons": set(), "quiz": {}, "points": {}})

    for lp in db.scalars(lq).all():
        row(lp.user_id)["lessons"].add(lp.lesson_id)
    for q in db.scalars(qq).all():
        best = row(q.user_id)["quiz"]
        best[q.lesson_id] = max(best.get(q.lesson_id, 0), q.score)
    for a in db.scalars(cq).all():
        if a.solved:
            pts = row(a.user_id)["points"]
            pts[a.challenge_id] = max(pts.get(a.challenge_id, 0), a.points)

    names = {u.id: u.name for u in db.scalars(select(User)).all()}
    rows = []
    for uid, d in agg.items():
        lessons = len(d["lessons"])
        quiz_correct = sum(d["quiz"].values())
        points = sum(d["points"].values())
        xp = XP_LESSON * lessons + XP_PER_CORRECT * quiz_correct + points
        if xp <= 0:
            continue
        rows.append({"user_id": uid, "name": names.get(uid, "Learner"), "xp": xp,
                     "lessons": lessons, "challenges": len(d["points"])})
    rows.sort(key=lambda r: (-r["xp"], r["name"]))
    for i, r in enumerate(rows):
        r["rank"] = i + 1
    return {"course": course, "entries": rows[:limit]}


# =============================================================== community chat
@router.get("/classrooms/{code}/chat")
def get_chat(code: str, after: int = 0, limit: int = 200, db: Session = Depends(get_session)) -> dict:
    code = code.upper()
    if not db.scalar(select(Classroom).where(Classroom.code == code)):
        raise HTTPException(404, "Classroom not found")
    q = select(ChatMessage).where(ChatMessage.classroom_code == code)
    if after:
        q = q.where(ChatMessage.id > after)
    rows = db.scalars(q.order_by(ChatMessage.id).limit(limit)).all()
    return {"messages": [{"id": m.id, "user_id": m.user_id, "name": m.name, "body": m.body,
                          "at": m.created_at.isoformat() if m.created_at else None} for m in rows]}


@router.post("/classrooms/{code}/chat")
def post_chat(code: str, body: ChatSend, db: Session = Depends(get_session)) -> dict:
    code = code.upper()
    if not db.scalar(select(Classroom).where(Classroom.code == code)):
        raise HTTPException(404, "Classroom not found")
    m = ChatMessage(classroom_code=code, user_id=body.user_id, name=body.name.strip()[:80], body=body.body.strip())
    db.add(m)
    db.commit()
    db.refresh(m)
    return {"id": m.id, "user_id": m.user_id, "name": m.name, "body": m.body,
            "at": m.created_at.isoformat() if m.created_at else None}


# =============================================================== course authoring
def _slug(title: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:32] or "course"
    return f"{base}-{_rand(4, string.ascii_lowercase + string.digits)}"


def _course_dict(c: AuthoredCourse, lessons: list[AuthoredLesson] | None = None) -> dict:
    out = {"id": c.id, "slug": c.slug, "title": c.title, "summary": c.summary,
           "instructor_id": c.instructor_id, "instructor_name": c.instructor_name, "price": c.price,
           "created_at": c.created_at.isoformat() if c.created_at else None}
    if lessons is not None:
        out["lessons"] = [{"id": l.id, "title": l.title, "video_url": l.video_url, "body": l.body, "order": l.order}
                          for l in lessons]
    return out


@router.post("/authoring/courses")
def create_authored_course(body: AuthoredCourseCreate, db: Session = Depends(get_session)) -> dict:
    teacher = db.get(User, body.instructor_id)
    if not teacher or teacher.role != "instructor":
        raise HTTPException(403, "Only instructors can create courses")
    c = AuthoredCourse(slug=_slug(body.title), title=body.title.strip(), summary=body.summary.strip(),
                       instructor_id=teacher.id, instructor_name=teacher.name, price=body.price)
    db.add(c)
    db.commit()
    db.refresh(c)
    return _course_dict(c, [])


@router.get("/authoring/courses")
def list_authored_courses(instructor_id: int | None = None, db: Session = Depends(get_session)) -> list[dict]:
    q = select(AuthoredCourse)
    if instructor_id:
        q = q.where(AuthoredCourse.instructor_id == instructor_id)
    rows = db.scalars(q.order_by(AuthoredCourse.created_at.desc())).all()
    counts = {}
    for cid, in db.execute(select(AuthoredLesson.course_id)).all():
        counts[cid] = counts.get(cid, 0) + 1
    return [{**_course_dict(c), "lesson_count": counts.get(c.id, 0)} for c in rows]


@router.get("/authoring/courses/{cid}")
def get_authored_course(cid: int, db: Session = Depends(get_session)) -> dict:
    c = db.get(AuthoredCourse, cid)
    if not c:
        raise HTTPException(404, "Course not found")
    lessons = db.scalars(select(AuthoredLesson).where(AuthoredLesson.course_id == cid).order_by(AuthoredLesson.order, AuthoredLesson.id)).all()
    return _course_dict(c, lessons)


@router.post("/authoring/courses/{cid}/lessons")
def add_authored_lesson(cid: int, body: AuthoredLessonCreate, db: Session = Depends(get_session)) -> dict:
    c = db.get(AuthoredCourse, cid)
    if not c:
        raise HTTPException(404, "Course not found")
    if c.instructor_id != body.instructor_id:
        raise HTTPException(403, "Only this course's instructor can add lessons")
    n = db.scalar(select(AuthoredLesson).where(AuthoredLesson.course_id == cid).order_by(AuthoredLesson.order.desc()))
    order = (n.order + 1) if n else 0
    l = AuthoredLesson(course_id=cid, title=body.title.strip(), video_url=(body.video_url or "").strip() or None,
                       body=body.body.strip(), order=order)
    db.add(l)
    db.commit()
    db.refresh(l)
    return {"id": l.id, "title": l.title, "video_url": l.video_url, "body": l.body, "order": l.order}


# =============================================================== tests / quizzes
@router.post("/tests")
def create_test(body: TestCreate, db: Session = Depends(get_session)) -> dict:
    teacher = db.get(User, body.instructor_id)
    if not teacher or teacher.role != "instructor":
        raise HTTPException(403, "Only instructors can create tests")
    t = Test(title=body.title.strip(), course=body.course, classroom_code=(body.classroom_code or None),
             instructor_id=teacher.id)
    db.add(t)
    db.flush()
    for i, q in enumerate(body.questions):
        if not (0 <= q.answer < len(q.options)):
            raise HTTPException(422, f"Question {i + 1}: answer index out of range")
        db.add(TestQuestion(test_id=t.id, prompt=q.prompt.strip(), options=q.options, answer=q.answer,
                            explain=q.explain.strip(), order=i))
    db.commit()
    return {"id": t.id, "title": t.title, "questions": len(body.questions)}


@router.get("/tests")
def list_tests(instructor_id: int | None = None, course: str | None = None,
               classroom_code: str | None = None, db: Session = Depends(get_session)) -> list[dict]:
    q = select(Test)
    if instructor_id:
        q = q.where(Test.instructor_id == instructor_id)
    if course:
        q = q.where(Test.course == course)
    if classroom_code:
        q = q.where(Test.classroom_code == classroom_code.upper())
    rows = db.scalars(q.order_by(Test.created_at.desc())).all()
    out = []
    for t in rows:
        n = len(db.scalars(select(TestQuestion).where(TestQuestion.test_id == t.id)).all())
        out.append({"id": t.id, "title": t.title, "course": t.course, "classroom_code": t.classroom_code,
                    "questions": n, "created_at": t.created_at.isoformat() if t.created_at else None})
    return out


@router.get("/tests/{tid}")
def get_test(tid: int, db: Session = Depends(get_session)) -> dict:
    t = db.get(Test, tid)
    if not t:
        raise HTTPException(404, "Test not found")
    qs = db.scalars(select(TestQuestion).where(TestQuestion.test_id == tid).order_by(TestQuestion.order, TestQuestion.id)).all()
    # answers are intentionally omitted so the test can be taken fairly
    return {"id": t.id, "title": t.title, "course": t.course, "classroom_code": t.classroom_code,
            "questions": [{"prompt": q.prompt, "options": q.options} for q in qs]}


@router.post("/tests/{tid}/submit")
def submit_test(tid: int, body: TestSubmit, db: Session = Depends(get_session)) -> dict:
    t = db.get(Test, tid)
    if not t:
        raise HTTPException(404, "Test not found")
    qs = db.scalars(select(TestQuestion).where(TestQuestion.test_id == tid).order_by(TestQuestion.order, TestQuestion.id)).all()
    results, score = [], 0
    for i, q in enumerate(qs):
        given = body.answers[i] if i < len(body.answers) else None
        ok = given == q.answer
        score += ok
        results.append({"correct": ok, "answer": q.answer, "explain": q.explain})
    total = len(qs)
    db.add(TestResult(test_id=tid, user_id=body.user_id, name=(body.name or "Guest")[:80], score=score, total=total))
    db.commit()
    return {"score": score, "total": total, "percent": round(100 * score / total) if total else 0, "results": results}


@router.get("/tests/{tid}/results")
def test_results(tid: int, db: Session = Depends(get_session)) -> list[dict]:
    rows = db.scalars(select(TestResult).where(TestResult.test_id == tid).order_by(TestResult.created_at.desc())).all()
    return [{"name": r.name, "score": r.score, "total": r.total,
             "percent": round(100 * r.score / r.total) if r.total else 0,
             "at": r.created_at.isoformat() if r.created_at else None} for r in rows]


# =============================================================== mini-projects
@router.get("/projects/{course}")
def course_projects(course: str, user_id: int | None = None, db: Session = Depends(get_session)) -> dict:
    items = P.for_course(course)
    submitted = set()
    if user_id:
        submitted = {s.project_id for s in db.scalars(
            select(ProjectSubmission).where(ProjectSubmission.user_id == user_id, ProjectSubmission.course == course)).all()}
    return {"course": course, "projects": [{**p, "submitted": p["id"] in submitted} for p in items]}


@router.post("/projects/{pid}/submit")
def submit_project(pid: str, body: ProjectSubmit, db: Session = Depends(get_session)) -> dict:
    cid, proj = P.find(pid)
    if not proj:
        raise HTTPException(404, "Project not found")
    user = db.get(User, body.user_id)
    if not user:
        raise HTTPException(404, "Sign in first to submit a project")
    s = ProjectSubmission(project_id=pid, course=cid, user_id=user.id, name=(body.name or user.name)[:80],
                          link=(body.link or "").strip() or None, note=body.note.strip())
    db.add(s)
    db.commit()
    return {"ok": True, "project": proj["title"]}


@router.get("/projects/{pid}/submissions")
def project_submissions(pid: str, db: Session = Depends(get_session)) -> list[dict]:
    rows = db.scalars(select(ProjectSubmission).where(ProjectSubmission.project_id == pid).order_by(ProjectSubmission.created_at.desc())).all()
    return [{"name": s.name, "link": s.link, "note": s.note,
             "at": s.created_at.isoformat() if s.created_at else None} for s in rows]


# =============================================================== leetcode practice
@router.get("/leetcode/{course}")
def leetcode_problems(course: str, user_id: int | None = None, db: Session = Depends(get_session)) -> dict:
    problems = leetcode.for_course(course)
    solved = set()
    if user_id:
        solved = {s.slug for s in db.scalars(select(PracticeSolved).where(PracticeSolved.user_id == user_id)).all()}
    return {"course": course, "problems": [{**p, "solved": p["slug"] in solved} for p in problems]}


@router.post("/leetcode/solve")
def leetcode_solve(body: PracticeSolve, db: Session = Depends(get_session)) -> dict:
    if not db.get(User, body.user_id):
        raise HTTPException(404, "Sign in first")
    existing = db.scalar(select(PracticeSolved).where(PracticeSolved.user_id == body.user_id, PracticeSolved.slug == body.slug))
    if body.solved and not existing:
        db.add(PracticeSolved(user_id=body.user_id, course=body.course, slug=body.slug))
    elif not body.solved and existing:
        db.delete(existing)
    db.commit()
    return {"ok": True, "solved": body.solved}


# =============================================================== institution / SSO
@router.post("/institutions")
def create_institution(body: InstitutionCreate, db: Session = Depends(get_session)) -> dict:
    code = _rand(6)
    while db.scalar(select(Institution).where(Institution.code == code)):
        code = _rand(6)
    inst = Institution(code=code, name=body.name.strip(), domain=(body.domain or "").strip() or None,
                       admin_name=body.admin_name.strip())
    db.add(inst)
    db.commit()
    return {"code": inst.code, "name": inst.name, "domain": inst.domain}


@router.post("/institutions/sso")
def sso_login(body: SsoLogin, db: Session = Depends(get_session)) -> dict:
    """Single sign-on style entry: an institution member signs in with the org code and their
    email. A platform user is created (or reused) and linked to the institution."""
    inst = db.scalar(select(Institution).where(Institution.code == body.code.upper()))
    if not inst:
        raise HTTPException(404, "Institution code not found")
    email = body.email.strip().lower()
    if inst.domain and not email.endswith("@" + inst.domain.lower().lstrip("@")):
        raise HTTPException(403, f"This institution only accepts @{inst.domain} email addresses")
    member = db.scalar(select(InstitutionMember).where(InstitutionMember.institution_id == inst.id, InstitutionMember.email == email))
    if member and member.user_id and db.get(User, member.user_id):
        user = db.get(User, member.user_id)
        user.name = body.name.strip()
    else:
        user = User(name=body.name.strip(), role=body.role)
        db.add(user)
        db.flush()
        if member:
            member.user_id = user.id
            member.name = body.name.strip()
            member.role = body.role
        else:
            db.add(InstitutionMember(institution_id=inst.id, user_id=user.id, name=body.name.strip(),
                                     email=email, role=body.role))
    db.commit()
    return {"user": {"id": user.id, "name": user.name, "role": user.role, "classroom_code": user.classroom_code},
            "institution": {"code": inst.code, "name": inst.name}}


@router.get("/institutions/{code}")
def institution_overview(code: str, db: Session = Depends(get_session)) -> dict:
    inst = db.scalar(select(Institution).where(Institution.code == code.upper()))
    if not inst:
        raise HTTPException(404, "Institution not found")
    members = db.scalars(select(InstitutionMember).where(InstitutionMember.institution_id == inst.id).order_by(InstitutionMember.created_at)).all()
    return {"code": inst.code, "name": inst.name, "domain": inst.domain, "admin_name": inst.admin_name,
            "members": [{"name": m.name, "email": m.email, "role": m.role,
                         "at": m.created_at.isoformat() if m.created_at else None} for m in members],
            "count": len(members)}
