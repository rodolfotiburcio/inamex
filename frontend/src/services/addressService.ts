import api from './api';
import { ApiResponse } from '../types/api';
import { Address, AddressCreate, AddressUpdate } from '../types/address';

export const addressService = {
  getAddresses: async (): Promise<ApiResponse<Address[]>> => {
    try {
      const response = await api.get('/addresses/');
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  getAddress: async (id: number): Promise<ApiResponse<Address>> => {
    try {
      const response = await api.get(`/addresses/${id}`);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  createAddress: async (data: AddressCreate): Promise<ApiResponse<Address>> => {
    try {
      const response = await api.post('/addresses/', data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  updateAddress: async (id: number, data: AddressUpdate): Promise<ApiResponse<Address>> => {
    try {
      const response = await api.put(`/addresses/${id}`, data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  deleteAddress: async (id: number): Promise<ApiResponse<void>> => {
    try {
      const response = await api.delete(`/addresses/${id}`);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },
}; 