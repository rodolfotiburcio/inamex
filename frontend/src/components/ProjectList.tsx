'use client';

import { useState, useEffect } from 'react';
import { Project, ProjectCreate, ProjectUpdate } from '../types/project';
import { Client } from '../types/client';
import { ProjectState, ProjectStateCreate, ProjectStateUpdate } from '../types/projectState';
import { projectService } from '../services/projectService';
import { clientService } from '../services/clientService';
import { projectStateService } from '../services/projectStateService';
import ProjectForm from './ProjectForm';
import ProjectStateForm from './ProjectStateForm';

export default function ProjectList() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [filteredProjects, setFilteredProjects] = useState<Project[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [projectStates, setProjectStates] = useState<ProjectState[]>([]);
  const [selectedStates, setSelectedStates] = useState<number[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showProjectForm, setShowProjectForm] = useState(false);
  const [showStateForm, setShowStateForm] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | undefined>(undefined);
  const [editingState, setEditingState] = useState<ProjectState | undefined>(undefined);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      const [projectsResponse, clientsResponse, projectStatesResponse] = await Promise.all([
        projectService.getProjects(),
        clientService.getClients(),
        projectStateService.getProjectStates(),
      ]);
      setProjects(projectsResponse.data);
      setFilteredProjects(projectsResponse.data);
      setClients(clientsResponse.data);
      setProjectStates(projectStatesResponse.data);
      setError(null);
    } catch (err) {
      setError('Error al cargar los datos');
      console.error('Error fetching data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (selectedStates.length === 0) {
      setFilteredProjects(projects);
    } else {
      setFilteredProjects(
        projects.filter(project => selectedStates.includes(project.state_id))
      );
    }
  }, [projects, selectedStates]);

  const handleCreate = async (data: ProjectCreate | ProjectUpdate) => {
    try {
      if ('name' in data && data.name) {
        await projectService.createProject(data as ProjectCreate);
        setShowProjectForm(false);
        fetchData();
      }
    } catch (err) {
      console.error('Error creating project:', err);
    }
  };

  const handleUpdate = async (data: ProjectUpdate) => {
    if (!editingProject) return;
    try {
      await projectService.updateProject(editingProject.id, data);
      setShowProjectForm(false);
      setEditingProject(undefined);
      fetchData();
    } catch (err) {
      console.error('Error updating project:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('¿Está seguro de que desea eliminar este proyecto?')) return;
    try {
      await projectService.deleteProject(id);
      fetchData();
    } catch (err) {
      console.error('Error deleting project:', err);
    }
  };

  const handleStateSubmit = async (data: ProjectStateCreate | ProjectStateUpdate) => {
    try {
      if (editingState) {
        await projectStateService.updateProjectState(editingState.id, data);
      } else {
        await projectStateService.createProjectState(data as ProjectStateCreate);
      }
      setShowStateForm(false);
      setEditingState(undefined);
      fetchData();
    } catch (err) {
      console.error('Error processing state:', err);
    }
  };

  const toggleStateFilter = (stateId: number) => {
    setSelectedStates(prev => {
      if (prev.includes(stateId)) {
        return prev.filter(id => id !== stateId);
      } else {
        return [...prev, stateId];
      }
    });
  };

  const handleEdit = (project: Project) => {
    setEditingProject(project);
    setShowProjectForm(true);
  };

  const getClientName = (clientId: number) => {
    const client = clients.find((c) => c.id === clientId);
    return client ? client.name : 'Cliente no encontrado';
  };

  const getProjectStateName = (stateId: number) => {
    const state = projectStates.find((s) => s.id === stateId);
    return state ? state.name : 'Estado no encontrado';
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    } catch {
      return 'Fecha no válida';
    }
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
      <div className="flex flex-col gap-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Proyectos</h1>
        <button
          onClick={() => {
            setEditingProject(undefined);
              setShowProjectForm(true);
          }}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Crear Proyecto
        </button>
      </div>

        <div className="flex flex-wrap gap-2 items-center">
          {projectStates.map((state) => (
            <div
              key={state.id}
              className={`flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                selectedStates.includes(state.id)
                  ? 'bg-blue-600 text-white'
                  : 'bg-blue-100 text-blue-800 hover:bg-blue-200'
              }`}
            >
              <button
                onClick={() => toggleStateFilter(state.id)}
                className="flex-grow"
              >
                {state.name}
              </button>
              <button
                onClick={() => {
                  setEditingState(state);
                  setShowStateForm(true);
                }}
                className="p-1 rounded-full hover:bg-white/20 transition-colors"
                title="Editar estado"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
              </button>
            </div>
          ))}
          <button
            onClick={() => {
              setEditingState(undefined);
              setShowStateForm(true);
            }}
            className="flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 hover:bg-green-200 transition-colors"
          >
            <span>+</span>
            <span>Nuevo Estado</span>
          </button>
        </div>
      </div>

      {showProjectForm && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full">
            <ProjectForm
              onSubmit={editingProject ? handleUpdate : handleCreate}
              onCancel={() => {
                setShowProjectForm(false);
                setEditingProject(undefined);
              }}
              initialData={editingProject}
              isEditing={!!editingProject}
            />
          </div>
        </div>
      )}

      {showStateForm && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <ProjectStateForm
              onSubmit={handleStateSubmit}
              onCancel={() => {
                setShowStateForm(false);
                setEditingState(undefined);
              }}
              initialData={editingState}
              isEditing={!!editingState}
            />
          </div>
        </div>
      )}

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {filteredProjects.map((project) => (
            <li key={project.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3">
                      <p className="text-sm font-medium text-gray-600">
                        #{project.number}
                      </p>
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {project.name}
                      </p>
                    </div>
                    <p className="mt-1 text-sm text-gray-500">
                      {project.description}
                    </p>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEdit(project)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Editar
                    </button>
                    <button
                      onClick={() => handleDelete(project.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Eliminar
                    </button>
                  </div>
                </div>
                <div className="mt-2 sm:flex sm:justify-between">
                  <div className="sm:flex space-x-6">
                    <p className="flex items-center text-sm text-gray-500">
                      Cliente: {getClientName(project.client_id)}
                    </p>
                    <p className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                      Estado: {getProjectStateName(project.state_id)}
                    </p>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                    <p>Fecha: {formatDate(project.date)}</p>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
} 