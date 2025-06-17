'use client';

import { useState, useEffect, useRef } from 'react';
import { Requirement, RequirementCreate, RequirementUpdate } from '../types/requirement';
import { RequirementState } from '../types/requirementState';
import { Project } from '../types/project';
import { projectService } from '../services/projectService';
import { Input, Button, Select, SelectItem } from '@heroui/react';

interface RequirementFormProps {
  onSubmit: (data: RequirementCreate | RequirementUpdate) => Promise<void>;
  onCancel: () => void;
  initialData?: Requirement;
  states: RequirementState[];
  isEditing?: boolean;
}

export default function RequirementForm({
  onSubmit,
  onCancel,
  initialData,
  states,
  isEditing = false,
}: RequirementFormProps) {
  const [formData, setFormData] = useState<RequirementCreate | RequirementUpdate>({
    project_id: undefined,
    request_date: new Date().toISOString().split('T')[0],
    requested_by: undefined,
    state_id: states.length > 0 ? states[0].id : 0,
    closing_date: undefined,
  });

  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoadingProjects, setIsLoadingProjects] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await projectService.getProjects();
        setProjects(response.data);
      } catch (error) {
        console.error('Error fetching projects:', error);
      } finally {
        setIsLoadingProjects(false);
      }
    };

    fetchProjects();
  }, []);

  useEffect(() => {
    if (initialData) {
      setFormData({
        project_id: initialData.project_id ?? undefined,
        request_date: initialData.request_date.split('T')[0],
        requested_by: initialData.requested_by ?? undefined,
        state_id: initialData.state_id,
        closing_date: initialData.closing_date ? initialData.closing_date.split('T')[0] : undefined,
      });

      if (initialData.project_id) {
        const project = projects.find(p => p.id === initialData.project_id);
        if (project) {
          setSelectedProject(project);
          setSearchTerm(`${project.number} - ${project.name}`);
        }
      }
    }
  }, [initialData, projects]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await onSubmit(formData);
      if (!isEditing) {
        setFormData({
          project_id: undefined,
          request_date: new Date().toISOString().split('T')[0],
          requested_by: undefined,
          state_id: states.length > 0 ? states[0].id : 0,
          closing_date: undefined,
        });
        setSearchTerm('');
        setSelectedProject(null);
      }
    } catch (error) {
      console.error('Error al procesar el formulario:', error);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value === '' ? undefined : type === 'number' ? Number(value) : value,
    }));
  };

  const handleProjectSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
    setShowDropdown(true);
    
    if (!value) {
      setFormData(prev => ({ ...prev, project_id: undefined }));
      setSelectedProject(null);
    }
  };

  const handleProjectSelect = (project: Project) => {
    setSelectedProject(project);
    setSearchTerm(`${project.number} - ${project.name}`);
    setFormData(prev => ({ ...prev, project_id: project.id }));
    setShowDropdown(false);
  };

  const filteredProjects = projects.filter(project => 
    `${project.number} - ${project.name}`.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="relative" ref={dropdownRef}>
        <label htmlFor="project_search" className="block text-sm font-medium text-content">
          Proyecto
        </label>
        <Input
          type="text"
          id="project_search"
          value={searchTerm}
          onChange={handleProjectSearch}
          onFocus={() => setShowDropdown(true)}
          placeholder="Buscar proyecto por número o nombre"
          className="mt-1"
          classNames={{
            input: 'bg-background text-content',
            label: 'text-content',
          }}
          autoComplete="off"
        />
        {showDropdown && searchTerm && (
          <div className="absolute z-10 w-full mt-1 bg-background rounded-md shadow-lg max-h-60 overflow-auto border border-background-foreground">
            {filteredProjects.length > 0 ? (
              <ul className="py-1">
                {filteredProjects.map((project) => (
                  <li
                    key={project.id}
                    onClick={() => handleProjectSelect(project)}
                    className="px-3 py-2 hover:bg-background-foreground cursor-pointer text-sm text-content"
                  >
                    <span className="font-medium">{project.number}</span>
                    <span className="text-content-foreground"> - {project.name}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="px-3 py-2 text-sm text-content-foreground">
                No se encontraron proyectos
              </div>
            )}
          </div>
        )}
      </div>

      <div>
        <label htmlFor="request_date" className="block text-sm font-medium text-content">
          Fecha de Solicitud
        </label>
        <Input
          type="date"
          id="request_date"
          name="request_date"
          value={formData.request_date}
          onChange={handleChange}
          required
          className="mt-1"
          classNames={{
            input: 'bg-background text-content',
            label: 'text-content',
          }}
        />
      </div>

      <div>
        <label htmlFor="requested_by" className="block text-sm font-medium text-content">
          Solicitado por (ID)
        </label>
        <Input
          type="number"
          id="requested_by"
          name="requested_by"
          value={formData.requested_by !== undefined ? formData.requested_by.toString() : ''}
          onChange={handleChange}
          placeholder="Ingrese el ID del solicitante"
          className="mt-1"
          classNames={{
            input: 'bg-background text-content',
            label: 'text-content',
          }}
        />
      </div>

      <div>
        <label htmlFor="state_id" className="block text-sm font-medium text-content">
          Estado
        </label>
        <Select
          id="state_id"
          name="state_id"
          selectedKeys={formData.state_id ? [formData.state_id.toString()] : []}
          onChange={(e) => {
            const value = e.target.value;
            setFormData(prev => ({
              ...prev,
              state_id: value ? parseInt(value, 10) : undefined
            }));
          }}
          required
          className="mt-1"
          classNames={{
            trigger: 'bg-background text-content',
            label: 'text-content',
          }}
        >
          {states.map((state) => (
            <SelectItem key={state.id.toString()}>
              {state.name}
            </SelectItem>
          ))}
        </Select>
      </div>

      <div>
        <label htmlFor="closing_date" className="block text-sm font-medium text-content">
          Fecha de Cierre
        </label>
        <Input
          type="date"
          id="closing_date"
          name="closing_date"
          value={formData.closing_date || ''}
          onChange={handleChange}
          className="mt-1"
          classNames={{
            input: 'bg-background text-content',
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
          {isEditing ? 'Guardar Cambios' : 'Crear Requerimiento'}
        </Button>
      </div>
    </form>
  );
} 