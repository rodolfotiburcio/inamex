import { Card, CardHeader, CardBody, Button } from '@heroui/react';

export default function Home() {
  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-gray-900 mb-6">
        Bienvenido al Sistema de Gestión
      </h1>
      
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card shadow="md" radius="lg" className="bg-white">
          <CardHeader>
            <span className="text-xl font-semibold text-gray-900">Usuarios</span>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              Gestiona los usuarios del sistema, incluyendo la creación, edición y eliminación de cuentas.
            </p>
            <Button color="primary" as="a" href="/users" fullWidth>
              Ir a Usuarios
            </Button>
          </CardBody>
        </Card>

        <Card shadow="md" radius="lg" className="bg-white">
          <CardHeader>
            <span className="text-xl font-semibold text-gray-900">Estados de Requerimientos</span>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              Administra los diferentes estados por los que puede pasar un requerimiento en el sistema.
            </p>
            <Button color="primary" as="a" href="/requirement-states" fullWidth>
              Ir a Estados de Requerimientos
            </Button>
          </CardBody>
        </Card>

        <Card shadow="md" radius="lg" className="bg-white">
          <CardHeader>
            <span className="text-xl font-semibold text-gray-900">Requerimientos</span>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              Gestiona los requerimientos del sistema, incluyendo su creación, seguimiento y actualización.
            </p>
            <Button color="primary" as="a" href="/requirements" fullWidth>
              Ir a Requerimientos
            </Button>
          </CardBody>
        </Card>
      </div>
    </main>
  );
}
