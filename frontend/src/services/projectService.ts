import api from './api';
import { ApiResponse } from '../types/api';
import { Project, ProjectCreate, ProjectUpdate } from '../types/project';

export const projectService = {
  // Obtener todos los proyectos
  getProjects: async (): Promise<ApiResponse<Project[]>> => {
    try {
      const response = await api.get('/projects/');
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Obtener un proyecto específico
  getProject: async (id: number): Promise<ApiResponse<Project>> => {
    try {
      const response = await api.get(`/projects/${id}`);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Crear un nuevo proyecto
  createProject: async (data: ProjectCreate): Promise<ApiResponse<Project>> => {
    try {
      const response = await api.post('/projects/', data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Actualizar un proyecto existente
  updateProject: async (id: number, data: ProjectUpdate): Promise<ApiResponse<Project>> => {
    try {
      const response = await api.put(`/projects/${id}`, data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Eliminar un proyecto
  deleteProject: async (id: number): Promise<ApiResponse<void>> => {
    try {
      const response = await api.delete(`/projects/${id}`);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },
}; 