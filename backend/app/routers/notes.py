from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.notes import Note, NoteFolder
from app.schemas.notes import (
    NoteFolderCreate,
    NoteFolderRead,
    NoteFolderTree,
    NoteFolderUpdate,
    NoteCreate,
    NoteRead,
    NoteSummary,
    NoteUpdate,
)

router = APIRouter()


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_descendant_ids(db: AsyncSession, folder_id: int) -> set[int]:
    """Return all descendant folder IDs (not including folder_id itself)."""
    all_result = await db.execute(select(NoteFolder.id, NoteFolder.parent_id))
    rows = all_result.all()
    children_map: dict[int, list[int]] = {}
    for fid, pid in rows:
        if pid is not None:
            children_map.setdefault(pid, []).append(fid)
    result: set[int] = set()
    queue = list(children_map.get(folder_id, []))
    while queue:
        fid = queue.pop()
        result.add(fid)
        queue.extend(children_map.get(fid, []))
    return result


# ── Folder endpoints ──────────────────────────────────────────────────────────

@router.get("/folders", response_model=list[NoteFolderTree])
async def list_folders(db: AsyncSession = Depends(get_db)):
    folder_result = await db.execute(select(NoteFolder).order_by(NoteFolder.name))
    folders = folder_result.scalars().all()

    count_result = await db.execute(
        select(Note.folder_id, func.count(Note.id).label("cnt"))
        .where(Note.folder_id.isnot(None))
        .group_by(Note.folder_id)
    )
    counts = {row.folder_id: row.cnt for row in count_result}

    # Build tree in Python to avoid N+1 queries
    folder_map: dict[int, dict] = {
        f.id: {
            "id": f.id,
            "name": f.name,
            "parent_id": f.parent_id,
            "note_count": counts.get(f.id, 0),
            "children": [],
            "created_at": f.created_at,
            "updated_at": f.updated_at,
        }
        for f in folders
    }
    roots: list[dict] = []
    for f in folders:
        node = folder_map[f.id]
        if f.parent_id is not None and f.parent_id in folder_map:
            folder_map[f.parent_id]["children"].append(node)
        else:
            roots.append(node)
    return roots


@router.get("/folders/unfiled-count")
async def unfiled_count(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(func.count(Note.id)).where(Note.folder_id.is_(None))
    )
    return {"count": result.scalar() or 0}


@router.post("/folders", response_model=NoteFolderRead, status_code=status.HTTP_201_CREATED)
async def create_folder(body: NoteFolderCreate, db: AsyncSession = Depends(get_db)):
    if body.parent_id is not None:
        parent = await db.get(NoteFolder, body.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent folder not found")
    folder = NoteFolder(name=body.name, parent_id=body.parent_id)
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return folder


@router.put("/folders/{folder_id}", response_model=NoteFolderRead)
async def update_folder(folder_id: int, body: NoteFolderUpdate, db: AsyncSession = Depends(get_db)):
    folder = await db.get(NoteFolder, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    updates = body.model_dump(exclude_unset=True)

    if "parent_id" in updates and updates["parent_id"] is not None:
        new_parent_id = updates["parent_id"]
        if new_parent_id == folder_id:
            raise HTTPException(status_code=422, detail="A folder cannot be its own parent")
        descendants = await _get_descendant_ids(db, folder_id)
        if new_parent_id in descendants:
            raise HTTPException(status_code=422, detail="Cannot move a folder into one of its own descendants")
        parent = await db.get(NoteFolder, new_parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent folder not found")

    for key, value in updates.items():
        setattr(folder, key, value)

    await db.commit()
    await db.refresh(folder)
    return folder


@router.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(folder_id: int, db: AsyncSession = Depends(get_db)):
    folder = await db.get(NoteFolder, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    parent_id = folder.parent_id

    # Re-parent direct child folders to this folder's parent (or null if root)
    child_result = await db.execute(
        select(NoteFolder).where(NoteFolder.parent_id == folder_id)
    )
    for child in child_result.scalars().all():
        child.parent_id = parent_id

    # Re-parent notes to this folder's parent (or null = Unfiled)
    note_result = await db.execute(
        select(Note).where(Note.folder_id == folder_id)
    )
    for note in note_result.scalars().all():
        note.folder_id = parent_id

    await db.delete(folder)
    await db.commit()


# ── Note endpoints ────────────────────────────────────────────────────────────

@router.get("", response_model=list[NoteSummary])
async def list_notes(
    folder_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(Note).order_by(Note.updated_at.desc())
    if folder_id == "unfiled":
        q = q.where(Note.folder_id.is_(None))
    elif folder_id is not None:
        try:
            q = q.where(Note.folder_id == int(folder_id))
        except ValueError:
            raise HTTPException(status_code=422, detail="folder_id must be an integer or 'unfiled'")
    result = await db.execute(q)
    return result.scalars().all()


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
async def create_note(body: NoteCreate, db: AsyncSession = Depends(get_db)):
    if body.folder_id is not None:
        folder = await db.get(NoteFolder, body.folder_id)
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
    note = Note(title=body.title, content=body.content, folder_id=body.folder_id)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


@router.get("/{note_id}", response_model=NoteRead)
async def get_note(note_id: int, db: AsyncSession = Depends(get_db)):
    note = await db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=NoteRead)
async def update_note(note_id: int, body: NoteUpdate, db: AsyncSession = Depends(get_db)):
    note = await db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    updates = body.model_dump(exclude_unset=True)

    if "folder_id" in updates and updates["folder_id"] is not None:
        folder = await db.get(NoteFolder, updates["folder_id"])
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")

    for key, value in updates.items():
        setattr(note, key, value)

    await db.commit()
    await db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: int, db: AsyncSession = Depends(get_db)):
    note = await db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    await db.delete(note)
    await db.commit()
