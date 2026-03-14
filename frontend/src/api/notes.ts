import type {
  Note,
  NoteCreate,
  NoteFolder,
  NoteFolderCreate,
  NoteFolderUpdate,
  NoteSummary,
  NoteUpdate,
} from "@/types/notes";

const BASE = "/api/notes";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const noteFolderApi = {
  tree: () => request<NoteFolder[]>(`${BASE}/folders`),

  unfiledCount: () => request<{ count: number }>(`${BASE}/folders/unfiled-count`),

  create: (data: NoteFolderCreate) =>
    request<NoteFolder>(`${BASE}/folders`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: number, data: NoteFolderUpdate) =>
    request<NoteFolder>(`${BASE}/folders/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (id: number) => request<void>(`${BASE}/folders/${id}`, { method: "DELETE" }),
};

export const noteApi = {
  list: (folderId?: number | "unfiled") => {
    const qs = folderId !== undefined ? `?folder_id=${folderId}` : "";
    return request<NoteSummary[]>(`${BASE}${qs}`);
  },

  get: (id: number) => request<Note>(`${BASE}/${id}`),

  create: (data: NoteCreate) =>
    request<Note>(`${BASE}`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: number, data: NoteUpdate) =>
    request<Note>(`${BASE}/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (id: number) => request<void>(`${BASE}/${id}`, { method: "DELETE" }),
};
