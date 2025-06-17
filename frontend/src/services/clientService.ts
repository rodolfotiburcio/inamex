import api from './api';
import { ApiResponse } from '../types/api';
import { Client, ClientCreate, ClientUpdate } from '../types/client';

export const clientService = {
  // Obtener todos los clientes
  getClients: async (): Promise<ApiResponse<Client[]>> => {
    try {
      const response = await api.get('/clients/');
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Obtener un cliente específico
  getClient: async (id: number): Promise<ApiResponse<Client>> => {
    try {
      const response = await api.get(`/clients/${id}`);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Crear un nuevo cliente
  createClient: async (data: ClientCreate): Promise<ApiResponse<Client>> => {
    try {
      const response = await api.post('/clients/', data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Actualizar un cliente existente
  updateClient: async (id: number, data: ClientUpdate): Promise<ApiResponse<Client>> => {
    try {
      const response = await api.put(`/clients/${id}`, data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Eliminar un cliente
  deleteClient: async (id: number): Promise<ApiResponse<void>> => {
    try {
      const response = await api.delete(`/clients/${id}`);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },
}; 