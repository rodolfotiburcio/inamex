export interface PaymentCondition {
  id: number;
  name: string;
  description: string | null;
  text: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaymentConditionCreate {
  name: string;
  description?: string;
  text: string;
  active?: boolean;
}

export interface PaymentConditionUpdate {
  name?: string;
  description?: string;
  text?: string;
  active?: boolean;
} 