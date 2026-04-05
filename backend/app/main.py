from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.tasks.router import categories_router, projects_router, tasks_router
from app.journal.router import journal_router, day_ratings_router
from app.finance.router import router as finance_router
from app.time_tracking.router import router as time_tracking_router
from app.timeline.router import router as timeline_router
from app.notes.router import router as notes_router
from app.health.router import router as health_router

app = FastAPI(
    title="MDEB Personal App",
    description="Self-hosted personal data manager",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/healthcheck")
async def healthcheck() -> dict:
    return {"status": "ok"}


app.include_router(categories_router, prefix="/api/categories", tags=["categories"])
app.include_router(projects_router, prefix="/api/projects", tags=["projects"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])
app.include_router(journal_router, prefix="/api/journal", tags=["journal"])
app.include_router(day_ratings_router, prefix="/api/day-ratings", tags=["day-ratings"])
app.include_router(finance_router, prefix="/api/finance", tags=["finance"])
app.include_router(time_tracking_router, prefix="/api/time", tags=["time"])
app.include_router(timeline_router, prefix="/api/timeline", tags=["timeline"])
app.include_router(notes_router, prefix="/api/notes", tags=["notes"])
app.include_router(health_router, prefix="/api/health", tags=["health"])
