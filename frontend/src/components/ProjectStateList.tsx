'use client';

import { useState, useEffect } from 'react';
import { ProjectState, ProjectStateCreate, ProjectStateUpdate } from '../types/projectState';
import { projectStateService } from '../services/projectStateService';
import ProjectStateForm from './ProjectStateForm';

export default function ProjectStateList() {
  const [projectStates, setProjectStates] = useState<ProjectState[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingProjectState, setEditingProjectState] = useState<ProjectState | undefined>(undefined);

  const fetchProjectStates = async () => {
    try {
      setIsLoading(true);
      const response = await projectStateService.getProjectStates();
      setProjectStates(response.data);
      setError(null);
    } catch (err) {
      setError('Error al cargar los estados de proyecto');
      console.error('Error fetching project states:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProjectStates();
  }, []);

  const handleCreate = async (data: ProjectStateCreate | ProjectStateUpdate) => {
    try {
      if ('name' in data && data.name) {
        await projectStateService.createProjectState(data as ProjectStateCreate);
        setShowForm(false);
        fetchProjectStates();
      }
    } catch (err) {
      console.error('Error creating project state:', err);
    }
  };

  const handleUpdate = async (data: ProjectStateUpdate) => {
    if (!editingProjectState) return;
    try {
      await projectStateService.updateProjectState(editingProjectState.id, data);
      setShowForm(false);
      setEditingProjectState(undefined);
      fetchProjectStates();
    } catch (err) {
      console.error('Error updating project state:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('¿Está seguro de que desea eliminar este estado de proyecto?')) return;
    try {
      await projectStateService.deleteProjectState(id);
      fetchProjectStates();
    } catch (err) {
      console.error('Error deleting project state:', err);
    }
  };

  const handleEdit = (projectState: ProjectState) => {
    setEditingProjectState(projectState);
    setShowForm(true);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">{error}</h3>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Estados de Proyecto</h1>
        <button
          onClick={() => {
            setEditingProjectState(undefined);
            setShowForm(true);
          }}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Crear Estado
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <ProjectStateForm
              onSubmit={editingProjectState ? handleUpdate : handleCreate}
              onCancel={() => {
                setShowForm(false);
                setEditingProjectState(undefined);
              }}
              initialData={editingProjectState}
              isEditing={!!editingProjectState}
            />
          </div>
        </div>
      )}

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {projectStates.map((projectState) => (
            <li key={projectState.id}>
              <div className="px-4 py-4 sm:px-6 flex items-center justify-between">
                <div className="flex items-center">
                  <p className="text-sm font-medium text-gray-900">{projectState.name}</p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEdit(projectState)}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    Editar
                  </button>
                  <button
                    onClick={() => handleDelete(projectState.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Eliminar
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
} 