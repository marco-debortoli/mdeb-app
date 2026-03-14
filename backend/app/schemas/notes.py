from datetime import datetime

from pydantic import BaseModel, Field


# ── NoteFolder ────────────────────────────────────────────────────────────────

class NoteFolderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    parent_id: int | None = None


class NoteFolderUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    parent_id: int | None = None


class NoteFolderRead(BaseModel):
    id: int
    name: str
    parent_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NoteFolderTree(BaseModel):
    """Folder with nested children and note count, for the folder tree endpoint."""
    id: int
    name: str
    parent_id: int | None
    note_count: int
    children: list["NoteFolderTree"]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


NoteFolderTree.model_rebuild()


# ── Note ──────────────────────────────────────────────────────────────────────

class NoteCreate(BaseModel):
    title: str = Field(default="Untitled", max_length=500)
    content: str = Field(default="")
    folder_id: int | None = None


class NoteUpdate(BaseModel):
    title: str | None = Field(None, max_length=500)
    content: str | None = None
    folder_id: int | None = None


class NoteSummary(BaseModel):
    """Lightweight schema for note list (no content body)."""
    id: int
    title: str
    folder_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    folder_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
