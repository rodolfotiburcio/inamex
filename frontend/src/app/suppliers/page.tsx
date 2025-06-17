'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Supplier } from '@/types/supplier';
import { supplierService } from '@/services/supplierService';
import { PaymentCondition } from '@/types/paymentCondition';
import { paymentConditionService } from '@/services/paymentConditionService';
import { Address } from '@/types/address';
import { addressService } from '@/services/addressService';

export default function SuppliersPage() {
  const router = useRouter();
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [paymentConditions, setPaymentConditions] = useState<PaymentCondition[]>([]);
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [suppliersResponse, paymentConditionsResponse, addressesResponse] = await Promise.all([
          supplierService.getSuppliers(),
          paymentConditionService.getPaymentConditions(),
          addressService.getAddresses(),
        ]);

        setSuppliers(suppliersResponse.data);
        setPaymentConditions(paymentConditionsResponse.data);
        setAddresses(addressesResponse.data);
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

  const getPaymentConditionName = (paymentConditionId: number) => {
    const condition = paymentConditions.find(pc => pc.id === paymentConditionId);
    return condition ? condition.name : 'Condición no encontrada';
  };

  const getAddressInfo = (addressId: number) => {
    const address = addresses.find(a => a.id === addressId);
    return address ? `${address.street} ${address.exterior_number}, ${address.neighborhood}` : 'Dirección no encontrada';
  };

  if (loading) {
    return <div className="text-center p-4">Cargando proveedores...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center p-4">{error}</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Proveedores</h1>
        <button
          onClick={() => router.push('/suppliers/new')}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
        >
          Nuevo Proveedor
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full border-collapse border border-gray-300">
          <thead>
            <tr className="bg-gray-100">
              <th className="border border-gray-300 px-4 py-2 text-left text-sm font-medium text-gray-700">ID</th>
              <th className="border border-gray-300 px-4 py-2 text-left text-sm font-medium text-gray-700">Dirección</th>
              <th className="border border-gray-300 px-4 py-2 text-left text-sm font-medium text-gray-700">Detalles Bancarios</th>
              <th className="border border-gray-300 px-4 py-2 text-left text-sm font-medium text-gray-700">Tiempo de Entrega</th>
              <th className="border border-gray-300 px-4 py-2 text-left text-sm font-medium text-gray-700">Condición de Pago</th>
              <th className="border border-gray-300 px-4 py-2 text-left text-sm font-medium text-gray-700">Moneda</th>
              <th className="border border-gray-300 px-4 py-2 text-left text-sm font-medium text-gray-700">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {suppliers.map((supplier) => (
              <tr key={supplier.id} className="hover:bg-gray-50">
                <td className="border border-gray-300 px-4 py-2 text-sm text-gray-700">{supplier.id}</td>
                <td className="border border-gray-300 px-4 py-2 text-sm text-gray-700">
                  <div>
                    <p className="font-medium">{getAddressInfo(supplier.address_id)}</p>
                    <p className="text-gray-600">{supplier.address}</p>
                  </div>
                </td>
                <td className="border border-gray-300 px-4 py-2 text-sm text-gray-700">{supplier.bank_details}</td>
                <td className="border border-gray-300 px-4 py-2 text-sm text-gray-700">{supplier.delivery_time}</td>
                <td className="border border-gray-300 px-4 py-2 text-sm text-gray-700">
                  {getPaymentConditionName(supplier.payment_condition_id)}
                </td>
                <td className="border border-gray-300 px-4 py-2 text-sm text-gray-700">{supplier.currency}</td>
                <td className="border border-gray-300 px-4 py-2 text-sm text-gray-700">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => router.push(`/suppliers/${supplier.id}`)}
                      className="p-1 rounded-full hover:bg-gray-100 transition-colors"
                      title="Ver detalle"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-5 w-5 text-green-600"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                        />
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                        />
                      </svg>
                    </button>
                    <button
                      onClick={() => router.push(`/suppliers/${supplier.id}/edit`)}
                      className="p-1 rounded-full hover:bg-gray-100 transition-colors"
                      title="Editar"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-5 w-5 text-blue-600"
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
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
} 