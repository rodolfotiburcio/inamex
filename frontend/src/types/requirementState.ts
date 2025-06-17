export interface RequirementState {
  id: number;
  name: string;
  description: string | null;
  order: number;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RequirementStateCreate {
  name: string;
  description?: string;
  order?: number;
  active?: boolean;
}

export interface RequirementStateUpdate {
  name?: string;
  description?: string;
  order?: number;
  active?: boolean;
} 