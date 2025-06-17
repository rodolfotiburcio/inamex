'use client';

import { useEffect, useState } from 'react';
import { User, UserCreate, UserUpdate } from '../types/user';
import { userService } from '../services/userService';
import UserForm from './UserForm';
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
} from '@heroui/react';

export default function UserList() {
  const { isOpen: isModalOpen, onOpen: openModal, onClose: closeModal } = useDisclosure();
  const { isOpen: isDeleteModalOpen, onOpen: openDeleteModal, onClose: closeDeleteModal } = useDisclosure();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [userToDelete, setUserToDelete] = useState<User | null>(null);

  const fetchUsers = async () => {
    try {
      const response = await userService.getUsers();
      setUsers(response.data);
      setError(null);
    } catch (err) {
      setError('Error al cargar los usuarios');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleSubmit = async (userData: UserCreate | UserUpdate) => {
    try {
      if (selectedUser) {
        await userService.updateUser(selectedUser.id, userData as UserUpdate);
      } else {
        await userService.createUser(userData as UserCreate);
      }
      closeModal();
      setSelectedUser(null);
      fetchUsers();
    } catch (err) {
      console.error('Error processing user:', err);
    }
  };

  const handleCreateClick = () => {
    setSelectedUser(null);
    openModal();
  };

  const handleDelete = async (user: User) => {
    setUserToDelete(user);
    openDeleteModal();
  };

  const confirmDelete = async () => {
    if (!userToDelete) return;
    try {
      await userService.deleteUser(userToDelete.id);
      closeDeleteModal();
      setUserToDelete(null);
      fetchUsers();
    } catch (err) {
      console.error('Error deleting user:', err);
    }
  };

  const openEditModal = (user: User) => {
    setSelectedUser(user);
    openModal();
  };

  if (loading) {
    return <div className="text-center p-4 text-content bg-background min-h-screen">Cargando usuarios...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center p-4 bg-background min-h-screen">{error}</div>;
  }

  return (
    <div className="container mx-auto p-4 bg-background min-h-screen">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-content">Lista de Usuarios</h2>
        <Button color="primary" onClick={handleCreateClick}>
          Crear Usuario
        </Button>
      </div>

      {/* Modal de Formulario */}
      <Modal 
        isOpen={isModalOpen} 
        onClose={closeModal} 
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
            {selectedUser ? 'Editar Usuario' : 'Crear Nuevo Usuario'}
          </ModalHeader>
          <ModalBody>
            <UserForm
              onSubmit={handleSubmit}
              onCancel={closeModal}
              initialData={selectedUser || undefined}
              isEditing={!!selectedUser}
            />
          </ModalBody>
        </ModalContent>
      </Modal>

      {/* Modal de Confirmación de Borrado */}
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
              ¿Estás seguro que deseas eliminar al usuario{' '}
              <span className="font-semibold">{userToDelete?.full_name}</span>? Esta acción no se puede deshacer.
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
        {users.map((user) => (
          <Card key={user.id} className="bg-background shadow border border-background-foreground">
            <CardHeader className="flex flex-row justify-between items-start">
              <div>
                <h3 className="font-semibold text-lg text-content">{user.full_name}</h3>
                <p className="text-content-foreground">{user.username}</p>
                <p className="text-sm text-content-foreground">
                  Creado: {new Date(user.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className="flex space-x-2">
                <Button
                  variant="light"
                  color="primary"
                  onClick={() => openEditModal(user)}
                  className="font-medium"
                >
                  Editar
                </Button>
                <Button
                  variant="light"
                  color="danger"
                  onClick={() => handleDelete(user)}
                  className="font-medium"
                >
                  Eliminar
                </Button>
              </div>
            </CardHeader>
            {/* Si quieres agregar más detalles, puedes usar <CardBody> aquí */}
          </Card>
        ))}
      </div>
    </div>
  );
} 