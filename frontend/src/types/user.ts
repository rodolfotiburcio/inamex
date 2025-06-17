export interface User {
  id: number;
  username: string;
  full_name: string;
  password_hash: string;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  username: string;
  full_name: string;
  password_hash: string;
}

export interface UserUpdate {
  username?: string;
  full_name?: string;
  password_hash?: string;
} 