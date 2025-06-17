'use client';

import { useState, useEffect } from 'react';
import { Project, ProjectCreate, ProjectUpdate } from '../types/project';
import { Client } from '../types/client';
import { ProjectState } from '../types/projectState';
import { clientService } from '../services/clientService';
import { projectStateService } from '../services/projectStateService';

interface ProjectFormProps {
  onSubmit: (data: ProjectCreate | ProjectUpdate) => Promise<void>;
  onCancel: () => void;
  initialData?: Project;
  isEditing?: boolean;
}

export default function ProjectForm({
  onSubmit,
  onCancel,
  initialData,
  isEditing = false,
}: ProjectFormProps) {
  const [formData, setFormData] = useState<ProjectCreate | ProjectUpdate>({
    name: '',
    description: '',
    client_id: 0,
    state_id: 0,
    number: '',
    date: new Date().toISOString(),
  });

  const [clients, setClients] = useState<Client[]>([]);
  const [projectStates, setProjectStates] = useState<ProjectState[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [clientsResponse, projectStatesResponse] = await Promise.all([
          clientService.getClients(),
          projectStateService.getProjectStates(),
        ]);
        setClients(clientsResponse.data);
        setProjectStates(projectStatesResponse.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name || '',
        description: initialData.description || '',
        client_id: initialData.client_id || 0,
        state_id: initialData.state_id || 0,
        number: initialData.number || '',
        date: initialData.date ? new Date(initialData.date).toISOString() : new Date().toISOString(),
      });
    }
  }, [initialData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        client_id: Number(formData.client_id),
        state_id: Number(formData.state_id),
      };
      await onSubmit(submitData);
      if (!isEditing) {
        setFormData({
          name: '',
          description: '',
          client_id: 0,
          state_id: 0,
          number: '',
          date: new Date().toISOString(),
        });
      }
    } catch (error) {
      console.error('Error al procesar el formulario:', error);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target;
    // Convertir la fecha local a ISO string
    const date = new Date(value);
    setFormData((prev) => ({
      ...prev,
      date: date.toISOString(),
    }));
  };

  const formatDateForInput = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toISOString().split('T')[0];
    } catch {
      return new Date().toISOString().split('T')[0];
    }
  };

  const inputClasses = "mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500";

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="number" className="block text-sm font-medium text-gray-900">
          Número de Proyecto
        </label>
        <input
          type="text"
          id="number"
          name="number"
          value={formData.number}
          onChange={handleChange}
          required
          placeholder="Ingrese el número del proyecto"
          className={inputClasses}
        />
      </div>

      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-900">
          Nombre del Proyecto
        </label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
          placeholder="Ingrese el nombre del proyecto"
          className={inputClasses}
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-900">
          Descripción
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          required
          placeholder="Ingrese la descripción del proyecto"
          className={inputClasses}
          rows={3}
        />
      </div>

      <div>
        <label htmlFor="date" className="block text-sm font-medium text-gray-900">
          Fecha
        </label>
        <input
          type="date"
          id="date"
          name="date"
          value={formatDateForInput(formData.date || new Date().toISOString())}
          onChange={handleDateChange}
          required
          className={inputClasses}
        />
      </div>

      <div>
        <label htmlFor="client_id" className="block text-sm font-medium text-gray-900">
          Cliente
        </label>
        <select
          id="client_id"
          name="client_id"
          value={formData.client_id}
          onChange={handleChange}
          required
          className={inputClasses}
        >
          <option value="">Seleccione un cliente</option>
          {clients.map((client) => (
            <option key={client.id} value={client.id}>
              {client.name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="state_id" className="block text-sm font-medium text-gray-900">
          Estado del Proyecto
        </label>
        <select
          id="state_id"
          name="state_id"
          value={formData.state_id}
          onChange={handleChange}
          required
          className={inputClasses}
        >
          <option value="">Seleccione un estado</option>
          {projectStates.map((state) => (
            <option key={state.id} value={state.id}>
              {state.name}
            </option>
          ))}
        </select>
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
          {isEditing ? 'Guardar Cambios' : 'Crear Proyecto'}
        </button>
      </div>
    </form>
  );
} 