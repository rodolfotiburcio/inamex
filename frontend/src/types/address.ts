export interface Address {
  id: number;
  street: string;
  exterior_number: string;
  interior_number: string | null;
  neighborhood: string;
  postal_code: string;
  city: string;
  state: string;
  country: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface AddressCreate {
  street: string;
  exterior_number: string;
  interior_number?: string;
  neighborhood: string;
  postal_code: string;
  city: string;
  state: string;
  country?: string;
  notes?: string;
}

export interface AddressUpdate {
  street?: string;
  exterior_number?: string;
  interior_number?: string;
  neighborhood?: string;
  postal_code?: string;
  city?: string;
  state?: string;
  country?: string;
  notes?: string;
} 