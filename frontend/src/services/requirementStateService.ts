import api from './api';
import { ApiResponse } from '../types/api';
import { RequirementState, RequirementStateCreate, RequirementStateUpdate } from '../types/requirementState';

export const requirementStateService = {
  // Obtener todos los estados
  getRequirementStates: async (): Promise<ApiResponse<RequirementState[]>> => {
    try {
      const response = await api.get('/requirement-states/');
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Crear un nuevo estado
  createRequirementState: async (data: RequirementStateCreate): Promise<ApiResponse<RequirementState>> => {
    try {
      const response = await api.post('/requirement-states/', data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Actualizar un estado existente
  updateRequirementState: async (stateId: number, data: RequirementStateUpdate): Promise<ApiResponse<RequirementState>> => {
    try {
      const response = await api.put(`/requirement-states/${stateId}`, data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Eliminar un estado
  deleteRequirementState: async (stateId: number): Promise<ApiResponse<void>> => {
    try {
      const response = await api.delete(`/requirement-states/${stateId}`);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },
}; 