import api from './api';
import { ApiResponse } from '../types/api';
import { User, UserCreate, UserUpdate } from '../types/user';

export const userService = {
  // Obtener todos los usuarios
  getUsers: async (): Promise<ApiResponse<User[]>> => {
    try {
      const response = await api.get('/users/');
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Crear un nuevo usuario
  createUser: async (userData: UserCreate): Promise<ApiResponse<User>> => {
    try {
      const response = await api.post('/users/', userData);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Actualizar un usuario existente
  updateUser: async (userId: number, userData: UserUpdate): Promise<ApiResponse<User>> => {
    try {
      const response = await api.put(`/users/${userId}`, userData);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Eliminar un usuario
  deleteUser: async (userId: number): Promise<ApiResponse<void>> => {
    try {
      const response = await api.delete(`/users/${userId}`);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },
}; 