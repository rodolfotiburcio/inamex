'use client';

import { useState, useEffect } from 'react';
import { UserCreate, UserUpdate, User } from '../types/user';
import { Input, Button } from '@heroui/react';

interface UserFormProps {
  onSubmit: (data: UserCreate | UserUpdate) => Promise<void>;
  onCancel: () => void;
  initialData?: User;
  isEditing?: boolean;
}

export default function UserForm({ onSubmit, onCancel, initialData, isEditing = false }: UserFormProps) {
  const [formData, setFormData] = useState<UserCreate | UserUpdate>({
    username: '',
    full_name: '',
    password_hash: '', // En un caso real, esto debería manejarse de manera más segura
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        username: initialData.username,
        full_name: initialData.full_name,
        // No incluimos el password_hash en la edición inicial
        password_hash: '',
      });
    }
  }, [initialData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Si estamos editando y no se ha modificado la contraseña, la eliminamos del envío
      if (isEditing && !formData.password_hash) {
        const { password_hash, ...dataWithoutPassword } = formData;
        await onSubmit(dataWithoutPassword);
      } else {
        await onSubmit(formData);
      }
      
      if (!isEditing) {
        // Solo limpiamos el formulario si estamos creando
        setFormData({
          username: '',
          full_name: '',
          password_hash: '',
        });
      }
    } catch (error) {
      console.error('Error al procesar el formulario:', error);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="username" className="block text-sm font-medium text-content">
          Nombre de usuario
        </label>
        <Input
          type="text"
          id="username"
          name="username"
          value={formData.username}
          onChange={handleChange}
          required
          placeholder="Ingrese el nombre de usuario"
          className="mt-1"
          classNames={{
            input: 'bg-background text-content border border-background-foreground focus:border-primary px-3 py-2 rounded-md',
            label: 'text-content',
          }}
        />
      </div>

      <div>
        <label htmlFor="full_name" className="block text-sm font-medium text-content">
          Nombre completo
        </label>
        <Input
          type="text"
          id="full_name"
          name="full_name"
          value={formData.full_name}
          onChange={handleChange}
          required
          placeholder="Ingrese el nombre completo"
          className="mt-1"
          classNames={{
            input: 'bg-background text-content border border-background-foreground focus:border-primary px-3 py-2 rounded-md',
            label: 'text-content',
          }}
        />
      </div>

      <div>
        <label htmlFor="password_hash" className="block text-sm font-medium text-content">
          {isEditing ? 'Nueva Contraseña (dejar en blanco para mantener la actual)' : 'Contraseña'}
        </label>
        <Input
          type="password"
          id="password_hash"
          name="password_hash"
          value={formData.password_hash}
          onChange={handleChange}
          required={!isEditing}
          placeholder={isEditing ? 'Dejar en blanco para mantener la contraseña actual' : 'Ingrese la contraseña'}
          className="mt-1"
          classNames={{
            input: 'bg-background text-content border border-background-foreground focus:border-primary px-3 py-2 rounded-md',
            label: 'text-content',
          }}
        />
      </div>

      <div className="flex justify-end space-x-2 pt-4">
        <Button
          variant="light"
          onClick={onCancel}
          className="text-content hover:bg-background-foreground"
        >
          Cancelar
        </Button>
        <Button
          color="primary"
          type="submit"
        >
          {isEditing ? 'Guardar Cambios' : 'Crear Usuario'}
        </Button>
      </div>
    </form>
  );
} 