export interface ArticleState {
  id: number;
  name: string;
  description: string | null;
  order: number;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ArticleStateCreate {
  name: string;
  description?: string | null;
  order?: number;
  active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface ArticleStateUpdate {
  name?: string | null;
  description?: string | null;
  order?: number | null;
  active?: boolean | null;
} 