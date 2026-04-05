from datetime import date, datetime

from pydantic import BaseModel, Field

from app.tasks.models import EffortLevel, Priority, TaskStatus


# ── Category ──────────────────────────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)
    color: str = Field("#4a7f3d", pattern=r"^#[0-9a-fA-F]{6}$")


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    color: str | None = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")


class CategoryRead(BaseModel):
    id: int
    name: str
    color: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Project ───────────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    description: str | None = None


class ProjectRead(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── TaskNote ──────────────────────────────────────────────────────────────────

class TaskNoteCreate(BaseModel):
    content: str = Field(..., min_length=1)


class TaskNoteRead(BaseModel):
    id: int
    task_id: int
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Task ──────────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    status: TaskStatus = TaskStatus.TODO
    effort: EffortLevel | None = None
    priority: Priority | None = None
    scheduled_date: date | None = None
    category_id: int | None = None
    project_id: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    status: TaskStatus | None = None
    effort: EffortLevel | None = None
    priority: Priority | None = None
    scheduled_date: date | None = None
    completed_date: date | None = None
    category_id: int | None = None
    project_id: int | None = None


class TaskRead(BaseModel):
    id: int
    title: str
    status: TaskStatus
    effort: EffortLevel | None
    priority: Priority | None
    scheduled_date: date | None
    completed_date: date | None
    category_id: int | None
    project_id: int | None
    created_at: datetime
    updated_at: datetime
    category: CategoryRead | None
    project: ProjectRead | None
    notes: list[TaskNoteRead]

    model_config = {"from_attributes": True}


class TaskSummary(BaseModel):
    """Lightweight task representation for list views (no notes)."""
    id: int
    title: str
    status: TaskStatus
    effort: EffortLevel | None
    priority: Priority | None
    scheduled_date: date | None
    completed_date: date | None
    category: CategoryRead | None
    project: ProjectRead | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
