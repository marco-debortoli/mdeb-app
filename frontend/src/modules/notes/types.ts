export interface NoteFolder {
  id: number;
  name: string;
  parent_id: number | null;
  note_count: number;
  children: NoteFolder[];
  created_at: string;
  updated_at: string;
}

export interface NoteFolderCreate {
  name: string;
  parent_id?: number | null;
}

export interface NoteFolderUpdate {
  name?: string;
  parent_id?: number | null;
}

export interface NoteSummary {
  id: number;
  title: string;
  folder_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface Note {
  id: number;
  title: string;
  content: string;
  folder_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface NoteCreate {
  title?: string;
  content?: string;
  folder_id?: number | null;
}

export interface NoteUpdate {
  title?: string;
  content?: string;
  folder_id?: number | null;
}

// Virtual folder sentinel for notes with no folder
export const UNFILED_FOLDER_ID = "unfiled" as const;
export type FolderSelection = number | typeof UNFILED_FOLDER_ID | null; // null = all notes
