'use client';

import { useState, useEffect } from 'react';
import { RequirementState, RequirementStateCreate, RequirementStateUpdate } from '../types/requirementState';
import { Button, Input } from '@heroui/react';

interface RequirementStateFormProps {
  onSubmit: (data: RequirementStateCreate | RequirementStateUpdate) => Promise<void>;
  onCancel: () => void;
  initialData?: RequirementState;
  isEditing?: boolean;
}

export default function RequirementStateForm({
  onSubmit,
  onCancel,
  initialData,
  isEditing = false,
}: RequirementStateFormProps) {
  const [formData, setFormData] = useState<RequirementStateCreate | RequirementStateUpdate>({
    name: '',
    description: '',
    order: 0,
    active: true,
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name,
        description: initialData.description || '',
        order: initialData.order,
        active: initialData.active,
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
          description: '',
          order: 0,
          active: true,
        });
      }
    } catch (error) {
      console.error('Error al procesar el formulario:', error);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const inputClasses = "mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500";

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="name" className="block text-sm font-medium">
          Nombre
        </label>
        <Input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
          placeholder="Ingrese el nombre del estado"
          className="mt-1"
          classNames={{
            input: 'bg-background text-content border border-background-foreground focus:border-primary px-3 py-2 rounded-md',
            label: 'text-content',
          }}
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium">
          Descripción
        </label>
        <Input
          as="textarea"
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={3}
          placeholder="Ingrese una descripción (opcional)"
          className="mt-1"
          classNames={{
            input: 'bg-background text-content border border-background-foreground focus:border-primary px-3 py-2 rounded-md',
            label: 'text-content',
          }}
        />
      </div>

      <div>
        <label htmlFor="order" className="block text-sm font-medium">
          Orden
        </label>
        <Input
          type="number"
          id="order"
          name="order"
          value={formData.order !== undefined ? formData.order.toString() : ''}
          onChange={handleChange}
          placeholder="Ingrese el orden"
          className="mt-1"
          classNames={{
            input: 'bg-background text-content border border-background-foreground focus:border-primary px-3 py-2 rounded-md',
            label: 'text-content',
          }}
        />
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="active"
          name="active"
          checked={formData.active}
          onChange={handleChange}
          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <label htmlFor="active" className="ml-2 block text-sm">
          Activo
        </label>
      </div>

      <div className="flex justify-end space-x-2 pt-4">
        <Button
          variant="light"
          type="button"
          onClick={onCancel}
          className="text-content hover:bg-background-foreground"
        >
          Cancelar
        </Button>
        <Button
          color="primary"
          type="submit"
        >
          {isEditing ? 'Guardar Cambios' : 'Crear Estado'}
        </Button>
      </div>
    </form>
  );
} 