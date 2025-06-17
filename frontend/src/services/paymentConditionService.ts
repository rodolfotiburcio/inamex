import api from './api';
import { ApiResponse } from '../types/api';
import { PaymentCondition, PaymentConditionCreate, PaymentConditionUpdate } from '../types/paymentCondition';

export const paymentConditionService = {
  getPaymentConditions: async (): Promise<ApiResponse<PaymentCondition[]>> => {
    try {
      const response = await api.get('/payment-conditions/');
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  getPaymentCondition: async (id: number): Promise<ApiResponse<PaymentCondition>> => {
    try {
      const response = await api.get(`/payment-conditions/${id}`);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  createPaymentCondition: async (data: PaymentConditionCreate): Promise<ApiResponse<PaymentCondition>> => {
    try {
      const response = await api.post('/payment-conditions/', data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  updatePaymentCondition: async (id: number, data: PaymentConditionUpdate): Promise<ApiResponse<PaymentCondition>> => {
    try {
      const response = await api.put(`/payment-conditions/${id}`, data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },

  deletePaymentCondition: async (id: number): Promise<ApiResponse<void>> => {
    try {
      const response = await api.delete(`/payment-conditions/${id}`);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw error;
    }
  },
}; 