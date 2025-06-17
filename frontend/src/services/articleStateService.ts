import api from './api';
import { ApiResponse } from '../types/api';
import { ArticleState, ArticleStateCreate, ArticleStateUpdate } from '../types/articleState';

export const articleStateService = {
  // Obtener todos los estados de artículos
  getArticleStates: async (): Promise<ApiResponse<ArticleState[]>> => {
    try {
      const response = await api.get('/article-states/');
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Obtener un estado de artículo específico
  getArticleState: async (id: number): Promise<ApiResponse<ArticleState>> => {
    try {
      const response = await api.get(`/article-states/${id}`);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Crear un nuevo estado de artículo
  createArticleState: async (data: ArticleStateCreate): Promise<ApiResponse<ArticleState>> => {
    try {
      const response = await api.post('/article-states/', data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Actualizar un estado de artículo existente
  updateArticleState: async (id: number, data: ArticleStateUpdate): Promise<ApiResponse<ArticleState>> => {
    try {
      const response = await api.put(`/article-states/${id}`, data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  // Eliminar un estado de artículo
  deleteArticleState: async (id: number): Promise<ApiResponse<void>> => {
    try {
      const response = await api.delete(`/article-states/${id}`);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },
}; 