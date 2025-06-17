'use client';

import { useState, useEffect, Fragment } from 'react';
import { useRouter } from 'next/navigation';
import { Dialog, Transition } from '@headlessui/react';
import { PlusIcon } from '@heroicons/react/24/outline';
import { SupplierCreate } from '@/types/supplier';
import { supplierService } from '@/services/supplierService';
import { PaymentCondition } from '@/types/paymentCondition';
import { paymentConditionService } from '@/services/paymentConditionService';
import { Address } from '@/types/address';
import { addressService } from '@/services/addressService';
import { AddressCreate } from '@/types/address';
import { PaymentConditionCreate } from '@/types/paymentCondition';

export default function NewSupplierPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<SupplierCreate>({
    name: '',
    rfc: '',
    address_id: 0,
    bank_details: '',
    delivery_time: '',
    payment_condition_id: 0,
    currency: 'MXN',
    notes: '',
  });

  const [addresses, setAddresses] = useState<Address[]>([]);
  const [paymentConditions, setPaymentConditions] = useState<PaymentCondition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddressModal, setShowAddressModal] = useState(false);
  const [showPaymentConditionModal, setShowPaymentConditionModal] = useState(false);
  const [newAddress, setNewAddress] = useState<AddressCreate>({
    street: '',
    exterior_number: '',
    interior_number: '',
    neighborhood: '',
    postal_code: '',
    city: '',
    state: '',
    country: 'Mexico',
    notes: '',
  });
  const [newPaymentCondition, setNewPaymentCondition] = useState<PaymentConditionCreate>({
    name: '',
    description: '',
    text: '',
    active: true,
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [addressesResponse, paymentConditionsResponse] = await Promise.all([
          addressService.getAddresses(),
          paymentConditionService.getPaymentConditions(),
        ]);

        setAddresses(addressesResponse.data);
        setPaymentConditions(paymentConditionsResponse.data);
        setError(null);
      } catch (err) {
        setError('Error al cargar los datos');
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await supplierService.createSupplier(formData);
      router.push('/suppliers');
    } catch (err) {
      setError('Error al crear el proveedor');
      console.error('Error creating supplier:', err);
    }
  };

  const handleAddressSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await addressService.createAddress(newAddress);
      setAddresses([...addresses, response.data]);
      setFormData({ ...formData, address_id: response.data.id });
      setShowAddressModal(false);
      setNewAddress({
        street: '',
        exterior_number: '',
        interior_number: '',
        neighborhood: '',
        postal_code: '',
        city: '',
        state: '',
        country: 'Mexico',
        notes: '',
      });
    } catch (err) {
      setError('Error al crear la dirección');
      console.error('Error creating address:', err);
    }
  };

  const handlePaymentConditionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await paymentConditionService.createPaymentCondition(newPaymentCondition);
      setPaymentConditions([...paymentConditions, response.data]);
      setFormData({ ...formData, payment_condition_id: response.data.id });
      setShowPaymentConditionModal(false);
      setNewPaymentCondition({
        name: '',
        description: '',
        text: '',
        active: true,
      });
    } catch (err) {
      setError('Error al crear la condición de pago');
      console.error('Error creating payment condition:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="md:flex md:items-center md:justify-between">
          <div className="min-w-0 flex-1">
            <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
              Nuevo Proveedor
            </h2>
          </div>
        </div>

        {error && (
          <div className="mt-4 rounded-md bg-red-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-8 space-y-8">
          <div className="space-y-8 divide-y divide-gray-200">
            <div className="space-y-6">
              <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                <div className="sm:col-span-3">
                  <label htmlFor="name" className="block text-sm font-medium text-gray-900">
                    Nombre
                  </label>
                  <div className="mt-1">
                    <input
                      type="text"
                      name="name"
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="block w-full rounded-md border-gray-300 bg-white text-gray-900 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      required
                    />
                  </div>
                </div>

                <div className="sm:col-span-3">
                  <label htmlFor="rfc" className="block text-sm font-medium text-gray-900">
                    RFC
                  </label>
                  <div className="mt-1">
                    <input
                      type="text"
                      name="rfc"
                      id="rfc"
                      value={formData.rfc}
                      onChange={(e) => setFormData({ ...formData, rfc: e.target.value })}
                      className="block w-full rounded-md border-gray-300 bg-white text-gray-900 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      required
                    />
                  </div>
                </div>

                <div className="sm:col-span-3">
                  <label htmlFor="address" className="block text-sm font-medium text-gray-900">
                    Dirección
                  </label>
                  <div className="mt-1 flex rounded-md shadow-sm">
                    <select
                      id="address"
                      name="address"
                      value={formData.address_id}
                      onChange={(e) => setFormData({ ...formData, address_id: Number(e.target.value) })}
                      className="block w-full rounded-l-md border-gray-300 bg-white text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      required
                    >
                      <option value="">Seleccione una dirección</option>
                      {addresses.map((address) => (
                        <option key={address.id} value={address.id}>
                          {address.street} {address.exterior_number}, {address.neighborhood}
                        </option>
                      ))}
                    </select>
                    <button
                      type="button"
                      onClick={() => setShowAddressModal(true)}
                      className="relative -ml-px inline-flex items-center space-x-2 rounded-r-md border border-gray-300 bg-gray-50 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    >
                      <PlusIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                      <span>Nueva</span>
                    </button>
                  </div>
                </div>

                <div className="sm:col-span-6">
                  <label htmlFor="bank_details" className="block text-sm font-medium text-gray-900">
                    Detalles Bancarios
                  </label>
                  <div className="mt-1">
                    <textarea
                      id="bank_details"
                      name="bank_details"
                      rows={3}
                      value={formData.bank_details}
                      onChange={(e) => setFormData({ ...formData, bank_details: e.target.value })}
                      className="block w-full rounded-md border-gray-300 bg-white text-gray-900 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      required
                    />
                  </div>
                </div>

                <div className="sm:col-span-3">
                  <label htmlFor="delivery_time" className="block text-sm font-medium text-gray-900">
                    Tiempo de Entrega
                  </label>
                  <div className="mt-1">
                    <input
                      type="text"
                      name="delivery_time"
                      id="delivery_time"
                      value={formData.delivery_time}
                      onChange={(e) => setFormData({ ...formData, delivery_time: e.target.value })}
                      className="block w-full rounded-md border-gray-300 bg-white text-gray-900 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      placeholder="Ej: 15 días hábiles"
                      required
                    />
                  </div>
                </div>

                <div className="sm:col-span-3">
                  <label htmlFor="payment_condition" className="block text-sm font-medium text-gray-900">
                    Condición de Pago
                  </label>
                  <div className="mt-1 flex rounded-md shadow-sm">
                    <select
                      id="payment_condition"
                      name="payment_condition"
                      value={formData.payment_condition_id}
                      onChange={(e) => setFormData({ ...formData, payment_condition_id: Number(e.target.value) })}
                      className="block w-full rounded-l-md border-gray-300 bg-white text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      required
                    >
                      <option value="">Seleccione una condición</option>
                      {paymentConditions.map((condition) => (
                        <option key={condition.id} value={condition.id}>
                          {condition.name}
                        </option>
                      ))}
                    </select>
                    <button
                      type="button"
                      onClick={() => setShowPaymentConditionModal(true)}
                      className="relative -ml-px inline-flex items-center space-x-2 rounded-r-md border border-gray-300 bg-gray-50 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    >
                      <PlusIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                      <span>Nueva</span>
                    </button>
                  </div>
                </div>

                <div className="sm:col-span-3">
                  <label htmlFor="currency" className="block text-sm font-medium text-gray-900">
                    Moneda
                  </label>
                  <div className="mt-1">
                    <select
                      id="currency"
                      name="currency"
                      value={formData.currency}
                      onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                      className="block w-full rounded-md border-gray-300 bg-white text-gray-900 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      required
                    >
                      <option value="MXN">MXN - Peso Mexicano</option>
                      <option value="USD">USD - Dólar Americano</option>
                      <option value="EUR">EUR - Euro</option>
                    </select>
                  </div>
                </div>

                <div className="sm:col-span-6">
                  <label htmlFor="notes" className="block text-sm font-medium text-gray-900">
                    Notas
                  </label>
                  <div className="mt-1">
                    <textarea
                      id="notes"
                      name="notes"
                      rows={3}
                      value={formData.notes || ''}
                      onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                      className="block w-full rounded-md border-gray-300 bg-white text-gray-900 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-5">
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => router.push('/suppliers')}
                className="rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="ml-3 inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >
                Crear Proveedor
              </button>
            </div>
          </div>
        </form>

        {/* Modal de Dirección */}
        <Transition.Root show={showAddressModal} as={Fragment}>
          <Dialog as="div" className="relative z-10" onClose={setShowAddressModal}>
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0"
              enterTo="opacity-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100"
              leaveTo="opacity-0"
            >
              <div className="fixed inset-0 bg-gray-100/75 backdrop-blur-sm transition-opacity" />
            </Transition.Child>

            <div className="fixed inset-0 z-10 overflow-y-auto">
              <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                <Transition.Child
                  as={Fragment}
                  enter="ease-out duration-300"
                  enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                  enterTo="opacity-100 translate-y-0 sm:scale-100"
                  leave="ease-in duration-200"
                  leaveFrom="opacity-100 translate-y-0 sm:scale-100"
                  leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                >
                  <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                    <div>
                      <div className="mt-3 text-center sm:mt-5">
                        <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900">
                          Nueva Dirección
                        </Dialog.Title>
                        <form onSubmit={handleAddressSubmit} className="mt-4 space-y-4">
                          <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                            <div className="sm:col-span-6">
                              <label htmlFor="street" className="block text-sm font-medium text-gray-700">
                                Calle
                              </label>
                              <div className="mt-1">
                                <input
                                  type="text"
                                  name="street"
                                  id="street"
                                  value={newAddress.street}
                                  onChange={(e) => setNewAddress({ ...newAddress, street: e.target.value })}
                                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                  required
                                />
                              </div>
                            </div>

                            <div className="sm:col-span-3">
                              <label htmlFor="exterior_number" className="block text-sm font-medium text-gray-700">
                                Número Exterior
                              </label>
                              <div className="mt-1">
                                <input
                                  type="text"
                                  name="exterior_number"
                                  id="exterior_number"
                                  value={newAddress.exterior_number}
                                  onChange={(e) => setNewAddress({ ...newAddress, exterior_number: e.target.value })}
                                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                  required
                                />
                              </div>
                            </div>

                            <div className="sm:col-span-3">
                              <label htmlFor="interior_number" className="block text-sm font-medium text-gray-700">
                                Número Interior
                              </label>
                              <div className="mt-1">
                                <input
                                  type="text"
                                  name="interior_number"
                                  id="interior_number"
                                  value={newAddress.interior_number || ''}
                                  onChange={(e) => setNewAddress({ ...newAddress, interior_number: e.target.value })}
                                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                />
                              </div>
                            </div>

                            <div className="sm:col-span-6">
                              <label htmlFor="neighborhood" className="block text-sm font-medium text-gray-700">
                                Colonia
                              </label>
                              <div className="mt-1">
                                <input
                                  type="text"
                                  name="neighborhood"
                                  id="neighborhood"
                                  value={newAddress.neighborhood}
                                  onChange={(e) => setNewAddress({ ...newAddress, neighborhood: e.target.value })}
                                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                  required
                                />
                              </div>
                            </div>

                            <div className="sm:col-span-3">
                              <label htmlFor="postal_code" className="block text-sm font-medium text-gray-700">
                                Código Postal
                              </label>
                              <div className="mt-1">
                                <input
                                  type="text"
                                  name="postal_code"
                                  id="postal_code"
                                  value={newAddress.postal_code}
                                  onChange={(e) => setNewAddress({ ...newAddress, postal_code: e.target.value })}
                                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                  required
                                />
                              </div>
                            </div>

                            <div className="sm:col-span-3">
                              <label htmlFor="city" className="block text-sm font-medium text-gray-700">
                                Ciudad
                              </label>
                              <div className="mt-1">
                                <input
                                  type="text"
                                  name="city"
                                  id="city"
                                  value={newAddress.city}
                                  onChange={(e) => setNewAddress({ ...newAddress, city: e.target.value })}
                                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                  required
                                />
                              </div>
                            </div>

                            <div className="sm:col-span-6">
                              <label htmlFor="state" className="block text-sm font-medium text-gray-700">
                                Estado
                              </label>
                              <div className="mt-1">
                                <input
                                  type="text"
                                  name="state"
                                  id="state"
                                  value={newAddress.state}
                                  onChange={(e) => setNewAddress({ ...newAddress, state: e.target.value })}
                                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                  required
                                />
                              </div>
                            </div>

                            <div className="sm:col-span-6">
                              <label htmlFor="address_notes" className="block text-sm font-medium text-gray-700">
                                Notas
                              </label>
                              <div className="mt-1">
                                <textarea
                                  id="address_notes"
                                  name="address_notes"
                                  rows={2}
                                  value={newAddress.notes || ''}
                                  onChange={(e) => setNewAddress({ ...newAddress, notes: e.target.value })}
                                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                />
                              </div>
                            </div>
                          </div>

                          <div className="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                            <button
                              type="submit"
                              className="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 sm:col-start-2"
                            >
                              Crear Dirección
                            </button>
                            <button
                              type="button"
                              onClick={() => setShowAddressModal(false)}
                              className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                            >
                              Cancelar
                            </button>
                          </div>
                        </form>
                      </div>
                    </div>
                  </Dialog.Panel>
                </Transition.Child>
              </div>
            </div>
          </Dialog>
        </Transition.Root>

        {/* Modal de Condición de Pago */}
        <Transition.Root show={showPaymentConditionModal} as={Fragment}>
          <Dialog as="div" className="relative z-10" onClose={setShowPaymentConditionModal}>
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0"
              enterTo="opacity-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100"
              leaveTo="opacity-0"
            >
              <div className="fixed inset-0 bg-gray-100/75 backdrop-blur-sm transition-opacity" />
            </Transition.Child>

            <div className="fixed inset-0 z-10 overflow-y-auto">
              <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                <Transition.Child
                  as={Fragment}
                  enter="ease-out duration-300"
                  enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                  enterTo="opacity-100 translate-y-0 sm:scale-100"
                  leave="ease-in duration-200"
                  leaveFrom="opacity-100 translate-y-0 sm:scale-100"
                  leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                >
                  <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                    <div>
                      <div className="mt-3 text-center sm:mt-5">
                        <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900">
                          Nueva Condición de Pago
                        </Dialog.Title>
                        <form onSubmit={handlePaymentConditionSubmit} className="mt-4 space-y-4">
                          <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                            <div className="sm:col-span-6">
                              <label htmlFor="condition_name" className="block text-sm font-medium text-gray-700">
                                Nombre
                              </label>
                              <div className="mt-1">
                                <input
                                  type="text"
                                  name="condition_name"
                                  id="condition_name"
                                  value={newPaymentCondition.name}
                                  onChange={(e) => setNewPaymentCondition({ ...newPaymentCondition, name: e.target.value })}
                                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                  required
                                />
                              </div>
                            </div>

                            <div className="sm:col-span-6">
                              <label htmlFor="condition_description" className="block text-sm font-medium text-gray-700">
                                Descripción
                              </label>
                              <div className="mt-1">
                                <textarea
                                  id="condition_description"
                                  name="condition_description"
                                  rows={2}
                                  value={newPaymentCondition.description || ''}
                                  onChange={(e) => setNewPaymentCondition({ ...newPaymentCondition, description: e.target.value })}
                                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                />
                              </div>
                            </div>

                            <div className="sm:col-span-6">
                              <label htmlFor="condition_text" className="block text-sm font-medium text-gray-700">
                                Texto de la Condición
                              </label>
                              <div className="mt-1">
                                <textarea
                                  id="condition_text"
                                  name="condition_text"
                                  rows={3}
                                  value={newPaymentCondition.text}
                                  onChange={(e) => setNewPaymentCondition({ ...newPaymentCondition, text: e.target.value })}
                                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                  required
                                />
                              </div>
                            </div>

                            <div className="sm:col-span-6">
                              <div className="flex items-center">
                                <input
                                  type="checkbox"
                                  id="condition_active"
                                  name="condition_active"
                                  checked={newPaymentCondition.active}
                                  onChange={(e) => setNewPaymentCondition({ ...newPaymentCondition, active: e.target.checked })}
                                  className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <label htmlFor="condition_active" className="ml-2 block text-sm text-gray-700">
                                  Activo
                                </label>
                              </div>
                            </div>
                          </div>

                          <div className="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                            <button
                              type="submit"
                              className="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 sm:col-start-2"
                            >
                              Crear Condición
                            </button>
                            <button
                              type="button"
                              onClick={() => setShowPaymentConditionModal(false)}
                              className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                            >
                              Cancelar
                            </button>
                          </div>
                        </form>
                      </div>
                    </div>
                  </Dialog.Panel>
                </Transition.Child>
              </div>
            </div>
          </Dialog>
        </Transition.Root>
      </div>
    </div>
  );
} 