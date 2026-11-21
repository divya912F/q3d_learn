# Q-3D Learn — v2.4 (Finale build)

New features added for the HackFront India finale. **Everything is additive** — no
existing screen, route or API was changed, only extended.

## New features
| Feature | Where | Backend |
|---|---|---|
| **Per-course leaderboards** | Sidebar → *Leaderboard* | `GET /api/leaderboard/{course}` (XP from lessons, quizzes, challenges) |
| **Community chat** | Sidebar → *Community* | `GET/POST /api/classrooms/{code}/chat` |
| **LeetCode Connect** | Sidebar → *Practice* | `GET /api/leetcode/{course}`, `POST /api/leetcode/solve` |
| **End-of-course mini-projects** | Course sub-nav → *Mini-projects* | `GET /api/projects/{course}`, `POST /api/projects/{id}/submit` |
| **Instructor tests / quiz builder** | Sidebar → *Tests* | `POST /api/tests`, `GET /api/tests/{id}`, `POST /api/tests/{id}/submit` |
| **Instructor course authoring (video)** | Sidebar → *Create course* | `POST /api/authoring/courses`, `.../lessons` |
| **Institution / SSO mode** | Sidebar → *Institution* | `POST /api/institutions`, `POST /api/institutions/sso` |
| **Multi-language (English / हिन्दी)** | Language picker in each new view | `frontend/js/i18n.js` |

## Run it
```bash
pip install -r requirements.txt
python run.py                 # http://localhost:8000   (API docs at /docs)
pytest                        # 118 existing tests + tests/test_finale.py
```

## Notes
- New database tables are created automatically on start-up (additive migration).
- Secrets are **never** committed. Copy `.env.example` → `.env` and add keys there
  (`.env` is gitignored). `AI_BOT_API_KEY` is read from the environment, config-ready.
- **Not included in this build (by request):** Sarvam AI voice, Neo4j, and the
  payment gateway. The instructor course model already carries a `price` field and a
  payment-gateway hook point on the instructor dashboard for when you add it.
