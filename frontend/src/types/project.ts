export interface Project {
  id: number;
  name: string;
  description: string;
  client_id: number;
  project_state_id: number;
  state_id: number;
  number: string;
  date: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description: string;
  client_id: number;
  state_id: number;
  number: string;
  date: string;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  client_id?: number;
  state_id?: number;
  number?: string;
  date?: string;
} 