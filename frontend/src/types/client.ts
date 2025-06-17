export interface Client {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface ClientCreate {
  name: string;
}

export interface ClientUpdate {
  name?: string;
} 