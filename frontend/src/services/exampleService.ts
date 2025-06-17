import api from './api';
import { ApiResponse } from '../types/api';

// Ejemplo de cómo crear un servicio para un endpoint específico
export const exampleService = {
  // Ejemplo de método GET
  getData: async (): Promise<ApiResponse<any>> => {
    try {
      const response = await api.get('/endpoint');
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Ejemplo de método POST
  postData: async (data: any): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/endpoint', data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },
}; 