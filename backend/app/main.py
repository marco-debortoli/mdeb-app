from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import categories, day_ratings, finance, health, journal, notes, projects, tasks, time_tracking, timeline

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


app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(journal.router, prefix="/api/journal", tags=["journal"])
app.include_router(day_ratings.router, prefix="/api/day-ratings", tags=["day-ratings"])
app.include_router(finance.router, prefix="/api/finance", tags=["finance"])
app.include_router(time_tracking.router, prefix="/api/time", tags=["time"])
app.include_router(timeline.router, prefix="/api/timeline", tags=["timeline"])
app.include_router(notes.router, prefix="/api/notes", tags=["notes"])
app.include_router(health.router, prefix="/api/health", tags=["health"])
