'use client';

import { useEffect, useState } from 'react';
import { RequirementState, RequirementStateCreate, RequirementStateUpdate } from '../types/requirementState';
import { requirementStateService } from '../services/requirementStateService';
import RequirementStateForm from './RequirementStateForm';

export default function RequirementStateList() {
  const [states, setStates] = useState<RequirementState[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedState, setSelectedState] = useState<RequirementState | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [stateToDelete, setStateToDelete] = useState<RequirementState | null>(null);

  const fetchStates = async () => {
    try {
      const response = await requirementStateService.getRequirementStates();
      // Ordenar los estados por el campo 'order'
      const sortedStates = response.data.sort((a, b) => a.order - b.order);
      setStates(sortedStates);
      setError(null);
    } catch (err) {
      setError('Error al cargar los estados');
      console.error('Error fetching states:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStates();
  }, []);

  const handleSubmit = async (data: RequirementStateCreate | RequirementStateUpdate) => {
    try {
      if (selectedState) {
        await requirementStateService.updateRequirementState(selectedState.id, data);
      } else {
        await requirementStateService.createRequirementState(data as RequirementStateCreate);
      }
      setIsModalOpen(false);
      setSelectedState(null);
      fetchStates();
    } catch (err) {
      console.error('Error processing state:', err);
    }
  };

  const handleDelete = async (state: RequirementState) => {
    setStateToDelete(state);
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    if (!stateToDelete) return;

    try {
      await requirementStateService.deleteRequirementState(stateToDelete.id);
      setShowDeleteConfirm(false);
      setStateToDelete(null);
      fetchStates();
    } catch (err) {
      console.error('Error deleting state:', err);
    }
  };

  const openEditModal = (state: RequirementState) => {
    setSelectedState(state);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedState(null);
  };

  if (loading) {
    return <div className="text-center p-4">Cargando estados...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center p-4">{error}</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Estados de Requerimientos</h2>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
        >
          Crear Estado
        </button>
      </div>

      {/* Modal de Formulario */}
      {isModalOpen && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div 
            className="absolute inset-0 bg-black opacity-75"
            onClick={closeModal}
          ></div>
          
          <div className="relative bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
            <div className="bg-gray-100 px-6 py-4 rounded-t-lg border-b">
              <h3 className="text-xl font-semibold text-gray-900">
                {selectedState ? 'Editar Estado' : 'Crear Nuevo Estado'}
              </h3>
            </div>

            <div className="px-6 py-4">
              <RequirementStateForm
                onSubmit={handleSubmit}
                onCancel={closeModal}
                initialData={selectedState || undefined}
                isEditing={!!selectedState}
              />
            </div>
          </div>
        </div>
      )}

      {/* Modal de Confirmación de Borrado */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div 
            className="absolute inset-0 bg-black opacity-75"
            onClick={() => setShowDeleteConfirm(false)}
          ></div>
          
          <div className="relative bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
            <div className="bg-gray-100 px-6 py-4 rounded-t-lg border-b">
              <h3 className="text-xl font-semibold text-gray-900">
                Confirmar Eliminación
              </h3>
            </div>

            <div className="px-6 py-4">
              <p className="text-gray-700 mb-4">
                ¿Estás seguro que deseas eliminar el estado{' '}
                <span className="font-semibold">{stateToDelete?.name}</span>?
                Esta acción no se puede deshacer.
              </p>

              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={confirmDelete}
                  className="px-4 py-2 text-white bg-red-600 rounded-md hover:bg-red-700 transition-colors"
                >
                  Eliminar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid gap-4">
        {states.map((state) => (
          <div
            key={state.id}
            className="bg-white shadow rounded-lg p-4 hover:shadow-lg transition-shadow"
          >
            <div className="flex justify-between items-start">
              <div className="flex-grow">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-lg text-gray-900">{state.name}</h3>
                  <span className="text-sm text-gray-500">Orden: {state.order}</span>
                  {!state.active && (
                    <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">
                      Inactivo
                    </span>
                  )}
                </div>
                {state.description && (
                  <p className="text-gray-700 mt-1">{state.description}</p>
                )}
                <p className="text-sm text-gray-500 mt-2">
                  Creado: {new Date(state.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => openEditModal(state)}
                  className="text-blue-600 hover:text-blue-800 transition-colors font-medium"
                >
                  Editar
                </button>
                <button
                  onClick={() => handleDelete(state)}
                  className="text-red-600 hover:text-red-800 transition-colors font-medium"
                >
                  Eliminar
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 