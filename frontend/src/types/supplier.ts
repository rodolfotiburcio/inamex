export interface Supplier {
  id: number;
  name: string;
  rfc: string;
  address: string;
  address_id: number;
  bank_details: string;
  delivery_time: string;
  payment_condition_id: number;
  currency: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface SupplierCreate {
  name: string;
  rfc: string;
  address_id: number;
  bank_details: string;
  delivery_time: string;
  payment_condition_id: number;
  currency: string;
  notes?: string;
}

export interface SupplierUpdate {
  name?: string;
  rfc?: string;
  address_id?: number;
  bank_details?: string;
  delivery_time?: string;
  payment_condition_id?: number;
  currency?: string;
  notes?: string;
} 