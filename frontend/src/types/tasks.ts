export enum TaskStatus {
  TODO = "TODO",
  IN_PROGRESS = "IN_PROGRESS",
  WAITING = "WAITING",
  COMPLETE = "COMPLETE",
  BACKLOG = "BACKLOG",
}

export enum EffortLevel {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
}

export enum Priority {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  URGENT = "URGENT",
}

export interface Category {
  id: number;
  name: string;
  color: string;
  created_at: string;
}

export interface Project {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
}

export interface TaskNote {
  id: number;
  task_id: number;
  content: string;
  created_at: string;
}

export interface Task {
  id: number;
  title: string;
  status: TaskStatus;
  effort: EffortLevel | null;
  priority: Priority | null;
  scheduled_date: string | null;
  completed_date: string | null;
  category_id: number | null;
  project_id: number | null;
  category: Category | null;
  project: Project | null;
  notes: TaskNote[];
  created_at: string;
  updated_at: string;
}

export interface TaskSummary {
  id: number;
  title: string;
  status: TaskStatus;
  effort: EffortLevel | null;
  priority: Priority | null;
  scheduled_date: string | null;
  completed_date: string | null;
  category: Category | null;
  project: Project | null;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  status?: TaskStatus;
  effort?: EffortLevel | null;
  priority?: Priority | null;
  scheduled_date?: string | null;
  category_id?: number | null;
  project_id?: number | null;
}

export interface TaskUpdate {
  title?: string;
  status?: TaskStatus;
  effort?: EffortLevel | null;
  priority?: Priority | null;
  scheduled_date?: string | null;
  completed_date?: string | null;
  category_id?: number | null;
  project_id?: number | null;
}

export interface TaskFilters {
  status: TaskStatus | "";
  category_id: number | "";
  project_id: number | "";
}
