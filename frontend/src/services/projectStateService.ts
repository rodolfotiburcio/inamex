import api from './api';
import { ApiResponse } from '../types/api';
import { ProjectState, ProjectStateCreate, ProjectStateUpdate } from '../types/projectState';

export const projectStateService = {
  // Obtener todos los estados de proyecto
  getProjectStates: async (): Promise<ApiResponse<ProjectState[]>> => {
    try {
      const response = await api.get('/project-states/');
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Obtener un estado de proyecto específico
  getProjectState: async (id: number): Promise<ApiResponse<ProjectState>> => {
    try {
      const response = await api.get(`/project-states/${id}`);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Crear un nuevo estado de proyecto
  createProjectState: async (data: ProjectStateCreate): Promise<ApiResponse<ProjectState>> => {
    try {
      const response = await api.post('/project-states/', data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Actualizar un estado de proyecto existente
  updateProjectState: async (id: number, data: ProjectStateUpdate): Promise<ApiResponse<ProjectState>> => {
    try {
      const response = await api.put(`/project-states/${id}`, data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Eliminar un estado de proyecto
  deleteProjectState: async (id: number): Promise<ApiResponse<void>> => {
    try {
      const response = await api.delete(`/project-states/${id}`);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },
}; 