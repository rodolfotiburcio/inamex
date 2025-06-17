import api from './api';
import { ApiResponse } from '../types/api';
import { Supplier, SupplierCreate, SupplierUpdate } from '../types/supplier';

export const supplierService = {
  getSuppliers: async (): Promise<ApiResponse<Supplier[]>> => {
    try {
      const response = await api.get('/suppliers/');
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  getSupplier: async (id: number): Promise<ApiResponse<Supplier>> => {
    try {
      const response = await api.get(`/suppliers/${id}`);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  createSupplier: async (data: SupplierCreate): Promise<ApiResponse<Supplier>> => {
    try {
      const response = await api.post('/suppliers/', data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  updateSupplier: async (id: number, data: SupplierUpdate): Promise<ApiResponse<Supplier>> => {
    try {
      const response = await api.put(`/suppliers/${id}`, data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  deleteSupplier: async (id: number): Promise<ApiResponse<void>> => {
    try {
      const response = await api.delete(`/suppliers/${id}`);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },
}; 