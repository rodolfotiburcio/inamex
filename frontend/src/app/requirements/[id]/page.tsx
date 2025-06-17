'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { use } from 'react';
import { Requirement } from '@/types/requirement';
import { requirementService } from '@/services/requirementService';
import { ArticleState } from '@/types/articleState';
import { articleStateService } from '@/services/articleStateService';
import { RequirementState } from '@/types/requirementState';
import { requirementStateService } from '@/services/requirementStateService';
import { Project } from '@/types/project';
import { projectService } from '@/services/projectService';
import { User } from '@/types/user';
import { userService } from '@/services/userService';

export default function RequirementDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const resolvedParams = use(params);
  const [requirement, setRequirement] = useState<Requirement | null>(null);
  const [articleStates, setArticleStates] = useState<ArticleState[]>([]);
  const [requirementStates, setRequirementStates] = useState<RequirementState[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const requirementId = parseInt(resolvedParams.id);
        if (isNaN(requirementId)) {
          setError('ID de requerimiento inválido');
          return;
        }

        const [
          requirementResponse,
          articleStatesResponse,
          requirementStatesResponse,
          projectsResponse,
          usersResponse,
        ] = await Promise.all([
          requirementService.getRequirement(requirementId),
          articleStateService.getArticleStates(),
          requirementStateService.getRequirementStates(),
          projectService.getProjects(),
          userService.getUsers(),
        ]);

        setRequirement(requirementResponse.data);
        setArticleStates(articleStatesResponse.data);
        setRequirementStates(requirementStatesResponse.data);
        setProjects(projectsResponse.data);
        setUsers(usersResponse.data);
        setError(null);
      } catch (err) {
        setError('Error al cargar los datos');
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [resolvedParams.id]);

  const getStateName = (stateId: number, states: (RequirementState | ArticleState)[]) => {
    const state = states.find(s => s.id === stateId);
    return state ? state.name : 'Estado desconocido';
  };

  const getProjectInfo = (projectId: number | null) => {
    if (!projectId) return null;
    const project = projects.find(p => p.id === projectId);
    return project ? `${project.number} - ${project.name}` : 'Proyecto no encontrado';
  };

  const getUserName = (userId: number | null) => {
    if (!userId) return null;
    const user = users.find(u => u.id === userId);
    return user ? user.full_name : 'Usuario no encontrado';
  };

  if (loading) {
    return <div className="text-center p-4">Cargando requerimiento...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center p-4">{error}</div>;
  }

  if (!requirement) {
    return <div className="text-center p-4">Requerimiento no encontrado</div>;
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto p-4">
        <div className="flex flex-col gap-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">
              Detalle del Requerimiento
            </h1>
            <button
              onClick={() => router.back()}
              className="bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300 transition-colors"
            >
              Volver
            </button>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h2 className="text-lg font-medium text-gray-900 mb-4">Información General</h2>
                <div className="space-y-2">
                  <p className="text-gray-700">
                    <span className="font-medium">ID:</span> {requirement.id}
                  </p>
                  <p className="text-gray-700">
                    <span className="font-medium">Estado:</span>{' '}
                    <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-sm">
                      {getStateName(requirement.state_id, requirementStates)}
                    </span>
                  </p>
                  <p className="text-gray-700">
                    <span className="font-medium">Fecha de Solicitud:</span>{' '}
                    {new Date(requirement.request_date).toLocaleDateString()}
                  </p>
                  {requirement.closing_date && (
                    <p className="text-gray-700">
                      <span className="font-medium">Fecha de Cierre:</span>{' '}
                      {new Date(requirement.closing_date).toLocaleDateString()}
                    </p>
                  )}
                  {requirement.project_id && (
                    <p className="text-gray-700">
                      <span className="font-medium">Proyecto:</span>{' '}
                      {getProjectInfo(requirement.project_id)}
                    </p>
                  )}
                  {requirement.requested_by && (
                    <p className="text-gray-700">
                      <span className="font-medium">Solicitado por:</span>{' '}
                      {getUserName(requirement.requested_by)}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {requirement.articles && requirement.articles.length > 0 && (
            <div className="bg-white shadow rounded-lg p-6">
              <div className="space-y-4">
                <h2 className="text-lg font-medium text-gray-900">Artículos</h2>
                <div className="overflow-x-auto">
                  <table className="min-w-full border-collapse border border-gray-300">
                    <thead>
                      <tr className="bg-gray-100">
                        <th className="border border-gray-300 px-4 py-2 text-left text-sm font-medium text-gray-700">Cantidad</th>
                        <th className="border border-gray-300 px-4 py-2 text-left text-sm font-medium text-gray-700">Unidad</th>
                        <th className="border border-gray-300 px-4 py-2 text-left text-sm font-medium text-gray-700">Marca</th>
                        <th className="border border-gray-300 px-4 py-2 text-left text-sm font-medium text-gray-700">Modelo</th>
                        <th className="border border-gray-300 px-4 py-2 text-left text-sm font-medium text-gray-700">Dimensiones</th>
                        <th className="border border-gray-300 px-4 py-2 text-left text-sm font-medium text-gray-700">Estado</th>
                        <th className="border border-gray-300 px-4 py-2 text-left text-sm font-medium text-gray-700">Notas</th>
                      </tr>
                    </thead>
                    <tbody>
                      {requirement.articles?.map((article) => (
                        <tr key={article.id} className="hover:bg-gray-50">
                          <td className="border border-gray-300 px-4 py-2 text-sm text-gray-700">{article.quantity}</td>
                          <td className="border border-gray-300 px-4 py-2 text-sm text-gray-700">{article.unit}</td>
                          <td className="border border-gray-300 px-4 py-2 text-sm text-gray-700">{article.brand}</td>
                          <td className="border border-gray-300 px-4 py-2 text-sm text-gray-700">{article.model}</td>
                          <td className="border border-gray-300 px-4 py-2 text-sm text-gray-700">{article.dimensions}</td>
                          <td className="border border-gray-300 px-4 py-2 text-sm text-gray-700">
                            <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full">
                              {getStateName(article.state_id, articleStates)}
                            </span>
                          </td>
                          <td className="border border-gray-300 px-4 py-2 text-sm text-gray-700">{article.notes || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
} 