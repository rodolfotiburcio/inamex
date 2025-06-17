import api from './api';
import { ApiResponse } from '../types/api';
import { Requirement, RequirementCreate, RequirementUpdate } from '../types/requirement';

export const requirementService = {
  // Obtener todos los requerimientos
  getRequirements: async (): Promise<ApiResponse<Requirement[]>> => {
    try {
      const response = await api.get('/requirements/');
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Obtener un requerimiento específico
  getRequirement: async (id: number): Promise<ApiResponse<Requirement>> => {
    try {
      const response = await api.get(`/requirements/${id}`);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Crear un nuevo requerimiento
  createRequirement: async (data: RequirementCreate): Promise<ApiResponse<Requirement>> => {
    try {
      const response = await api.post('/requirements/', data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Eliminar un requerimiento
  deleteRequirement: async (id: number): Promise<ApiResponse<void>> => {
    try {
      const response = await api.delete(`/requirements/${id}`);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Crear un requerimiento con artículos
  createRequirementWithArticles: async (data: {
    requirement: RequirementCreate;
    articles: Array<{
      quantity: number;
      unit: string;
      brand: string;
      model: string;
      dimensions: string;
      state_id: number;
      notes: string;
    }>;
  }): Promise<ApiResponse<Requirement>> => {
    try {
      const response = await api.post('/requirements/with-articles', data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },
}; 