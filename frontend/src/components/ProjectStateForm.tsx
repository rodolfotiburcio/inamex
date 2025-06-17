'use client';

import { useState, useEffect } from 'react';
import { ProjectState, ProjectStateCreate, ProjectStateUpdate } from '../types/projectState';

interface ProjectStateFormProps {
  onSubmit: (data: ProjectStateCreate | ProjectStateUpdate) => Promise<void>;
  onCancel: () => void;
  initialData?: ProjectState;
  isEditing?: boolean;
}

export default function ProjectStateForm({
  onSubmit,
  onCancel,
  initialData,
  isEditing = false,
}: ProjectStateFormProps) {
  const [formData, setFormData] = useState<ProjectStateCreate | ProjectStateUpdate>({
    name: '',
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name,
      });
    }
  }, [initialData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await onSubmit(formData);
      if (!isEditing) {
        setFormData({
          name: '',
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

  const inputClasses = "mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500";

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-900">
          Nombre del Estado
        </label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
          placeholder="Ingrese el nombre del estado"
          className={inputClasses}
        />
      </div>

      <div className="flex justify-end space-x-2 pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Cancelar
        </button>
        <button
          type="submit"
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          {isEditing ? 'Guardar Cambios' : 'Crear Estado'}
        </button>
      </div>
    </form>
  );
} 