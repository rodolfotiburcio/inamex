'use client';

import { useEffect, useState } from 'react';
import { Requirement, RequirementCreate, RequirementUpdate } from '../types/requirement';
import { RequirementState, RequirementStateCreate, RequirementStateUpdate } from '../types/requirementState';
import { requirementService } from '../services/requirementService';
import { requirementStateService } from '../services/requirementStateService';
import RequirementForm from './RequirementForm';
import RequirementStateForm from './RequirementStateForm';
import { Project } from '../types/project';
import { projectService } from '../services/projectService';
import { useRouter } from 'next/navigation';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Modal,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalContent,
  useDisclosure,
  Chip,
} from '@heroui/react';
import { PencilIcon, TrashIcon } from '@heroicons/react/24/outline';

export default function RequirementList() {
  const router = useRouter();
  const { isOpen: isRequirementModalOpen, onOpen: openRequirementModal, onClose: closeRequirementModal } = useDisclosure();
  const { isOpen: isStateModalOpen, onOpen: openStateModal, onClose: closeStateModal } = useDisclosure();
  const { isOpen: isDeleteModalOpen, onOpen: openDeleteModal, onClose: closeDeleteModal } = useDisclosure();
  
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [filteredRequirements, setFilteredRequirements] = useState<Requirement[]>([]);
  const [states, setStates] = useState<RequirementState[]>([]);
  const [selectedStates, setSelectedStates] = useState<number[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRequirement, setSelectedRequirement] = useState<Requirement | null>(null);
  const [selectedState, setSelectedState] = useState<RequirementState | null>(null);
  const [requirementToDelete, setRequirementToDelete] = useState<Requirement | null>(null);

  const fetchRequirements = async () => {
    try {
      const response = await requirementService.getRequirements();
      setRequirements(response.data);
      setError(null);
    } catch (err) {
      setError('Error al cargar los requerimientos');
      console.error('Error fetching requirements:', err);
    }
  };

  const fetchStates = async () => {
    try {
      const response = await requirementStateService.getRequirementStates();
      setStates(response.data);
    } catch (err) {
      console.error('Error fetching states:', err);
      setError('Error al cargar los estados');
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await projectService.getProjects();
      setProjects(response.data);
    } catch (err) {
      console.error('Error fetching projects:', err);
      setError('Error al cargar los proyectos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    Promise.all([fetchRequirements(), fetchStates(), fetchProjects()]);
  }, []);

  useEffect(() => {
    if (selectedStates.length === 0) {
      setFilteredRequirements(requirements);
    } else {
      setFilteredRequirements(
        requirements.filter(req => selectedStates.includes(req.state_id))
      );
    }
  }, [requirements, selectedStates]);

  const handleSubmit = async (data: RequirementCreate | RequirementUpdate) => {
    try {
      if (selectedRequirement) {
        // La API no soporta actualización de requerimientos
        // await requirementService.updateRequirement(selectedRequirement.id, data);
      } else {
        await requirementService.createRequirement(data as RequirementCreate);
      }
      closeRequirementModal();
      setSelectedRequirement(null);
      fetchRequirements();
    } catch (err) {
      console.error('Error processing requirement:', err);
    }
  };

  const handleDelete = async (requirement: Requirement) => {
    setRequirementToDelete(requirement);
    openDeleteModal();
  };

  const confirmDelete = async () => {
    if (!requirementToDelete) return;
    try {
      await requirementService.deleteRequirement(requirementToDelete.id);
      closeDeleteModal();
      setRequirementToDelete(null);
      fetchRequirements();
    } catch (err) {
      console.error('Error deleting requirement:', err);
    }
  };

  const getStateName = (stateId: number) => {
    const state = states.find(s => s.id === stateId);
    return state ? state.name : 'Estado desconocido';
  };

  const getProjectInfo = (projectId: number | null) => {
    if (!projectId) return null;
    const project = projects.find(p => p.id === projectId);
    return project ? `${project.number} - ${project.name}` : 'Proyecto no encontrado';
  };

  const handleStateSubmit = async (data: RequirementStateCreate | RequirementStateUpdate) => {
    try {
      if (selectedState) {
        await requirementStateService.updateRequirementState(selectedState.id, data);
      } else {
        await requirementStateService.createRequirementState(data as RequirementStateCreate);
      }
      closeStateModal();
      setSelectedState(null);
      fetchStates();
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

  const handleEdit = (requirement: Requirement) => {
    setSelectedRequirement(requirement);
    openRequirementModal();
  };

  if (loading) {
    return <div className="text-center p-4 text-content bg-background min-h-screen">Cargando requerimientos...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center p-4 bg-background min-h-screen">{error}</div>;
  }

  return (
    <div className="container mx-auto p-4 bg-background min-h-screen">
      <div className="flex flex-col gap-4 mb-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-content">Requerimientos</h2>
          <Button 
            color="primary" 
            onClick={() => router.push('/requirements/with-articles')}
          >
            Crear Requerimiento
          </Button>
        </div>

        <div className="flex flex-wrap gap-2 items-center">
          {states.map((state) => (
            <Chip
              key={state.id}
              variant="flat"
              color={state.active ? "primary" : "default"}
              className={`cursor-pointer ${
                selectedStates.includes(state.id) ? 'opacity-100' : 'opacity-70'
              }`}
              onClick={() => toggleStateFilter(state.id)}
              endContent={
                <Button
                  isIconOnly
                  variant="light"
                  size="sm"
                  onClick={() => {
                    setSelectedState(state);
                    openStateModal();
                  }}
                >
                  <PencilIcon className="w-4 h-4" />
                </Button>
              }
            >
              {state.name}
            </Chip>
          ))}
          <Button
            variant="flat"
            color="success"
            onClick={() => {
              setSelectedState(null);
              openStateModal();
            }}
          >
            + Nuevo Estado
          </Button>
        </div>
      </div>

      {/* Requirement Modal */}
      <Modal 
        isOpen={isRequirementModalOpen} 
        onClose={closeRequirementModal} 
        size="md"
        backdrop="blur"
        classNames={{
          base: "bg-background text-content",
          header: "border-b border-background-foreground",
          body: "py-6",
          footer: "border-t border-background-foreground",
          backdrop: "bg-background/40 backdrop-blur-sm"
        }}
      >
        <ModalContent>
          <ModalHeader className="flex flex-col gap-1">
            {selectedRequirement ? 'Editar Requerimiento' : 'Crear Nuevo Requerimiento'}
          </ModalHeader>
          <ModalBody>
            <RequirementForm
              onSubmit={handleSubmit}
              onCancel={closeRequirementModal}
              initialData={selectedRequirement || undefined}
              states={states}
              isEditing={!!selectedRequirement}
            />
          </ModalBody>
        </ModalContent>
      </Modal>

      {/* State Modal */}
      <Modal 
        isOpen={isStateModalOpen} 
        onClose={closeStateModal} 
        size="md"
        backdrop="blur"
        classNames={{
          base: "bg-background text-content",
          header: "border-b border-background-foreground",
          body: "py-6",
          footer: "border-t border-background-foreground",
          backdrop: "bg-background/40 backdrop-blur-sm"
        }}
      >
        <ModalContent>
          <ModalHeader className="flex flex-col gap-1">
            {selectedState ? 'Editar Estado' : 'Crear Nuevo Estado'}
          </ModalHeader>
          <ModalBody>
            <RequirementStateForm
              onSubmit={handleStateSubmit}
              onCancel={closeStateModal}
              initialData={selectedState || undefined}
              isEditing={!!selectedState}
            />
          </ModalBody>
        </ModalContent>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal 
        isOpen={isDeleteModalOpen} 
        onClose={closeDeleteModal} 
        size="sm"
        backdrop="blur"
        classNames={{
          base: "bg-background text-content",
          header: "border-b border-background-foreground",
          body: "py-6",
          footer: "border-t border-background-foreground",
          backdrop: "bg-background/40 backdrop-blur-sm"
        }}
      >
        <ModalContent>
          <ModalHeader>Confirmar Eliminación</ModalHeader>
          <ModalBody>
            <p className="text-content-foreground mb-4">
              ¿Estás seguro que deseas eliminar el requerimiento{' '}
              <span className="font-semibold">{requirementToDelete?.id}</span>? Esta acción no se puede deshacer.
            </p>
          </ModalBody>
          <ModalFooter>
            <Button variant="light" onClick={closeDeleteModal}>
              Cancelar
            </Button>
            <Button color="danger" onClick={confirmDelete}>
              Eliminar
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      <div className="grid gap-4">
        {filteredRequirements.map((requirement) => (
          <Card key={requirement.id} className="bg-background shadow border border-background-foreground">
            <CardHeader className="flex flex-row justify-between items-start">
              <div>
                <h3 className="font-semibold text-lg text-content">
                  Requerimiento {requirement.id}
                </h3>
                <p className="text-content-foreground">
                  Proyecto: {getProjectInfo(requirement.project_id)}
                </p>
                <p className="text-sm text-content-foreground">
                  Estado: {getStateName(requirement.state_id)}
                </p>
                <p className="text-sm text-content-foreground">
                  Fecha: {new Date(requirement.request_date).toLocaleDateString()}
                </p>
              </div>
              <div className="flex space-x-2">
                <Button
                  isIconOnly
                  variant="light"
                  color="primary"
                  onClick={() => handleEdit(requirement)}
                >
                  <PencilIcon className="w-5 h-5" />
                </Button>
                <Button
                  isIconOnly
                  variant="light"
                  color="danger"
                  onClick={() => handleDelete(requirement)}
                >
                  <TrashIcon className="w-5 h-5" />
                </Button>
              </div>
            </CardHeader>
          </Card>
        ))}
      </div>
    </div>
  );
} 