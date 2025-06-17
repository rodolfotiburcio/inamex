// Aquí definiremos los tipos de datos que usaremos con la API
export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

// Ejemplo de tipo para una respuesta de error
export interface ApiError {
  message: string;
  status: number;
  errors?: Record<string, string[]>;
} 