export interface Requirement {
  id: number;
  project_id: number | null;
  request_date: string;
  requested_by: number | null;
  state_id: number;
  closing_date: string | null;
  articles?: Article[];
}

export interface Article {
  id: number;
  requirement_id: number | null;
  requirement_consecutive: number | null;
  quantity: string;
  unit: string;
  brand: string;
  model: string;
  dimensions: string;
  state_id: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface RequirementCreate {
  project_id?: number;
  request_date?: string;
  requested_by?: number;
  state_id: number;
  closing_date?: string;
}

export interface RequirementUpdate {
  project_id?: number;
  request_date?: string;
  requested_by?: number;
  state_id?: number;
  closing_date?: string;
}

// Tipo extendido para mostrar información relacionada
export interface RequirementWithDetails extends Requirement {
  project_name?: string;
  requester_name?: string;
  state_name?: string;
} 