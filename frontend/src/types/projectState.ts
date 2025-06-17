export interface ProjectState {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectStateCreate {
  name: string;
}

export interface ProjectStateUpdate {
  name?: string;
} 