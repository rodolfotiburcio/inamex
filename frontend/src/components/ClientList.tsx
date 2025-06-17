'use client';

import { useState, useEffect } from 'react';
import { Client, ClientCreate, ClientUpdate } from '../types/client';
import { clientService } from '../services/clientService';
import ClientForm from './ClientForm';

export default function ClientList() {
  const [clients, setClients] = useState<Client[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingClient, setEditingClient] = useState<Client | undefined>(undefined);

  const fetchClients = async () => {
    try {
      setIsLoading(true);
      const response = await clientService.getClients();
      setClients(response.data);
      setError(null);
    } catch (err) {
      setError('Error al cargar los clientes');
      console.error('Error fetching clients:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchClients();
  }, []);

  const handleCreate = async (data: ClientCreate | ClientUpdate) => {
    try {
      if ('name' in data && data.name) {
        await clientService.createClient(data as ClientCreate);
        setShowForm(false);
        fetchClients();
      }
    } catch (err) {
      console.error('Error creating client:', err);
    }
  };

  const handleUpdate = async (data: ClientUpdate) => {
    if (!editingClient) return;
    try {
      await clientService.updateClient(editingClient.id, data);
      setShowForm(false);
      setEditingClient(undefined);
      fetchClients();
    } catch (err) {
      console.error('Error updating client:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('¿Está seguro de que desea eliminar este cliente?')) return;
    try {
      await clientService.deleteClient(id);
      fetchClients();
    } catch (err) {
      console.error('Error deleting client:', err);
    }
  };

  const handleEdit = (client: Client) => {
    setEditingClient(client);
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
        <h1 className="text-2xl font-bold text-gray-900">Clientes</h1>
        <button
          onClick={() => {
            setEditingClient(undefined);
            setShowForm(true);
          }}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Crear Cliente
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <ClientForm
              onSubmit={editingClient ? handleUpdate : handleCreate}
              onCancel={() => {
                setShowForm(false);
                setEditingClient(undefined);
              }}
              initialData={editingClient}
              isEditing={!!editingClient}
            />
          </div>
        </div>
      )}

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {clients.map((client) => (
            <li key={client.id}>
              <div className="px-4 py-4 sm:px-6 flex items-center justify-between">
                <div className="flex items-center">
                  <p className="text-sm font-medium text-gray-900">{client.name}</p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEdit(client)}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    Editar
                  </button>
                  <button
                    onClick={() => handleDelete(client.id)}
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