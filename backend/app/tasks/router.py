from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.tasks.models import Category, Project, Task, TaskNote, TaskStatus
from app.tasks.schemas import (
    CategoryCreate, CategoryRead, CategoryUpdate,
    ProjectCreate, ProjectRead, ProjectUpdate,
    TaskCreate, TaskNoteCreate, TaskNoteRead, TaskRead, TaskSummary, TaskUpdate,
)

categories_router = APIRouter()
projects_router = APIRouter()
tasks_router = APIRouter()


# ── Categories ────────────────────────────────────────────────────────────────

@categories_router.get("", response_model=list[CategoryRead])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).order_by(Category.name))
    return result.scalars().all()


@categories_router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(body: CategoryCreate, db: AsyncSession = Depends(get_db)):
    category = Category(**body.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@categories_router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int, body: CategoryUpdate, db: AsyncSession = Depends(get_db)
):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(category, field, value)
    await db.commit()
    await db.refresh(category)
    return category


@categories_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(category)
    await db.commit()


# ── Projects ──────────────────────────────────────────────────────────────────

@projects_router.get("", response_model=list[ProjectRead])
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).order_by(Project.name))
    return result.scalars().all()


@projects_router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(body: ProjectCreate, db: AsyncSession = Depends(get_db)):
    project = Project(**body.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@projects_router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int, body: ProjectUpdate, db: AsyncSession = Depends(get_db)
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(project, field, value)
    await db.commit()
    await db.refresh(project)
    return project


@projects_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
    await db.commit()


# ── Tasks ─────────────────────────────────────────────────────────────────────

def _load_task_relations():
    return selectinload(Task.category), selectinload(Task.project), selectinload(Task.notes)


@tasks_router.get("", response_model=list[TaskSummary])
async def list_tasks(
    status_filter: TaskStatus | None = Query(None, alias="status"),
    category_id: int | None = Query(None),
    project_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(Task).options(selectinload(Task.category), selectinload(Task.project))
    if status_filter is not None:
        q = q.where(Task.status == status_filter)
    if category_id is not None:
        q = q.where(Task.category_id == category_id)
    if project_id is not None:
        q = q.where(Task.project_id == project_id)
    q = q.order_by(Task.created_at.desc())
    result = await db.execute(q)
    return result.scalars().all()


@tasks_router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(body: TaskCreate, db: AsyncSession = Depends(get_db)):
    task = Task(**body.model_dump())
    if task.status == TaskStatus.COMPLETE:
        task.completed_date = date.today()
    db.add(task)
    await db.commit()
    await db.refresh(task)
    # Reload with relations
    result = await db.execute(
        select(Task).where(Task.id == task.id).options(*_load_task_relations())
    )
    return result.scalar_one()


@tasks_router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Task).where(Task.id == task_id).options(*_load_task_relations())
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@tasks_router.put("/{task_id}", response_model=TaskRead)
async def update_task(task_id: int, body: TaskUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Task).where(Task.id == task_id).options(*_load_task_relations())
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(task, field, value)

    # Auto-manage completed_date (only when the client didn't supply one explicitly)
    if "status" in updates and "completed_date" not in updates:
        if task.status == TaskStatus.COMPLETE and task.completed_date is None:
            task.completed_date = date.today()
        elif task.status != TaskStatus.COMPLETE:
            task.completed_date = None

    await db.commit()
    result = await db.execute(
        select(Task).where(Task.id == task_id).options(*_load_task_relations())
    )
    return result.scalar_one()


@tasks_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()


# ── Task Notes ────────────────────────────────────────────────────────────────

@tasks_router.post("/{task_id}/notes", response_model=TaskNoteRead, status_code=status.HTTP_201_CREATED)
async def add_note(task_id: int, body: TaskNoteCreate, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    note = TaskNote(task_id=task_id, content=body.content)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


@tasks_router.delete("/{task_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(task_id: int, note_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TaskNote).where(TaskNote.id == note_id, TaskNote.task_id == task_id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    await db.delete(note)
    await db.commit()
