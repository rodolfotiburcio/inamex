'use client';

import { useState, useEffect, useRef } from 'react';
import { RequirementCreate } from '../types/requirement';
import { requirementService } from '../services/requirementService';
import { useRouter } from 'next/navigation';
import { Project } from '../types/project';
import { projectService } from '../services/projectService';
import { RequirementState } from '../types/requirementState';
import { requirementStateService } from '../services/requirementStateService';
import { User } from '../types/user';
import { userService } from '../services/userService';
import { ArticleState } from '../types/articleState';
import { articleStateService } from '../services/articleStateService';
import { Input, Button, Divider, DatePicker, Autocomplete, AutocompleteItem } from '@heroui/react';
import { parseDate } from '@internationalized/date';

interface Article {
  id?: number;
  quantity: number;
  unit: string;
  brand: string;
  model: string;
  dimensions: string;
  state_id: number;
  notes: string;
}

interface RequirementWithArticles {
  requirement: RequirementCreate;
  articles: Article[];
}

export default function RequirementWithArticlesForm() {
  const router = useRouter();
  const [formData, setFormData] = useState<RequirementWithArticles>({
    requirement: {
      project_id: 0,
      request_date: new Date().toISOString().split('T')[0],
      requested_by: 0,
      state_id: 0,
      closing_date: '',
    },
    articles: [],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [filteredProjects, setFilteredProjects] = useState<Project[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [states, setStates] = useState<RequirementState[]>([]);
  const [articleStates, setArticleStates] = useState<ArticleState[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [projectsResponse, statesResponse, articleStatesResponse, usersResponse] = await Promise.all([
          projectService.getProjects(),
          requirementStateService.getRequirementStates(),
          articleStateService.getArticleStates(),
          userService.getUsers()
        ]);
        setProjects(projectsResponse.data);
        setStates(statesResponse.data);
        setArticleStates(articleStatesResponse.data);
        setUsers(usersResponse.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    const defaultDate = new Date();
    defaultDate.setDate(defaultDate.getDate() + 7);
    setFormData(prev => ({
      ...prev,
      requirement: {
        ...prev.requirement,
        request_date: defaultDate.toISOString().split('T')[0],
      },
    }));
  }, []);

  useEffect(() => {
    if (searchTerm) {
      const searchWords = searchTerm.toLowerCase().split(/\s+/).filter(word => word.length > 0);
      const filtered = projects.filter(project => {
        const projectText = `${project.number} ${project.name}`.toLowerCase();
        return searchWords.every(word => projectText.includes(word));
      });
      setFilteredProjects(filtered);
      setShowDropdown(true);
    } else {
      setFilteredProjects([]);
      setShowDropdown(false);
    }
  }, [searchTerm, projects]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleProjectSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
    
    if (!value) {
      setFormData(prev => ({ ...prev, requirement: { ...prev.requirement, project_id: 0 } }));
      setSelectedProject(null);
    }
  };

  const handleProjectSelect = (project: Project) => {
    setSelectedProject(project);
    setSearchTerm(`${project.number} - ${project.name}`);
    setFormData(prev => ({ ...prev, requirement: { ...prev.requirement, project_id: project.id } }));
    setShowDropdown(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      console.log('Form data being sent:', JSON.stringify(formData, null, 2));
      await requirementService.createRequirementWithArticles(formData);
      router.push('/requirements');
    } catch (err) {
      console.error('Error submitting form:', err);
      setError('Error al crear el requerimiento. Por favor, intente nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleRequirementChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      requirement: {
        ...prev.requirement,
        [name]: name === 'project_id' || name === 'requested_by' || name === 'state_id' 
          ? Number(value)
          : value,
      },
    }));
  };

  const handleArticleChange = (
    index: number,
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => {
      const newArticles = [...prev.articles];
      newArticles[index] = {
        ...newArticles[index],
        [name]: name === 'quantity' || name === 'state_id' 
          ? Number(value)
          : value,
      };
      return {
        ...prev,
        articles: newArticles,
      };
    });
  };

  const addArticle = () => {
    setFormData(prev => ({
      ...prev,
      articles: [
        ...prev.articles,
        {
          quantity: 1,
          unit: '',
          brand: '',
          model: '',
          dimensions: '',
          state_id: articleStates.length > 0 ? articleStates[0].id : 0,
          notes: '',
        },
      ],
    }));
  };

  const removeArticle = (index: number) => {
    setFormData(prev => ({
      ...prev,
      articles: prev.articles.filter((_, i) => i !== index),
    }));
  };

  const animals = [
  {label: "Cat", key: "cat", description: "The second most popular pet in the world"},
  {label: "Dog", key: "dog", description: "The most popular pet in the world"},
  {label: "Elephant", key: "elephant", description: "The largest land animal"},
  {label: "Lion", key: "lion", description: "The king of the jungle"},
  {label: "Tiger", key: "tiger", description: "The largest cat species"},
  {label: "Giraffe", key: "giraffe", description: "The tallest land animal"},
  {
    label: "Dolphin",
    key: "dolphin",
    description: "A widely distributed and diverse group of aquatic mammals",
  },
  {label: "Penguin", key: "penguin", description: "A group of aquatic flightless birds"},
  {label: "Zebra", key: "zebra", description: "A several species of African equids"},
  {
    label: "Shark",
    key: "shark",
    description: "A group of elasmobranch fish characterized by a cartilaginous skeleton",
  },
  {
    label: "Whale",
    key: "whale",
    description: "Diverse group of fully aquatic placental marine mammals",
  },
  {label: "Otter", key: "otter", description: "A carnivorous mammal in the subfamily Lutrinae"},
  {label: "Crocodile", key: "crocodile", description: "A large semiaquatic reptile"},
];


  return (
    <div className="container mx-auto p-4 min-h-screen bg-background">
      <h2 className="text-2xl font-bold mb-6">Nuevo Requerimiento con Artículos</h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        <Divider />

        <div className="shadow rounded-lg">
          <h2 className="text-lg font-medium mb-4">
            Información del Requerimiento
          </h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <Autocomplete
                id="project_search"
                name="project_search"
                label="Proyecto"
                labelPlacement="outside"
                selectedKey={selectedProject ? selectedProject.id.toString() : ''}
                onSelectionChange={(key) => {
                  const project = projects.find(p => p.id.toString() === key);
                  if (project) {
                    setSelectedProject(project);
                    setSearchTerm(`${project.number} - ${project.name}`);
                    setFormData(prev => ({
                      ...prev,
                      requirement: {
                        ...prev.requirement,
                        project_id: project.id,
                      },
                    }));
                  }
                }}
                inputValue={searchTerm}
                onInputChange={setSearchTerm}
                className="mt-1"
                classNames={{
                  base: 'w-full bg-background text-content focus:border-primary px-3 py-2 rounded-md',
                  listboxWrapper: '',
                }}
                placeholder="Buscar proyecto por número o nombre"
                aria-label="Proyecto"
                allowsCustomValue={false}
                variant="bordered"
              >
                {projects
                  .filter(project =>
                    `${project.number} - ${project.name}`
                      .toLowerCase()
                      .includes(searchTerm.toLowerCase())
                  )
                  .map(project => (
                    <AutocompleteItem key={project.id.toString()}>
                      {project.number} - {project.name}
                    </AutocompleteItem>
                  ))}
              </Autocomplete>
            </div>
            <div className="relative">
              <label htmlFor="request_date" className="block text-sm font-medium text-content">
                Fecha de Solicitud
              </label>
              
              <DatePicker
                id="request_date"
                name="request_date"
                value={formData.requirement.request_date ? parseDate(formData.requirement.request_date) : null}
                onChange={(dateValue) => {
                  setFormData((prev) => ({
                    ...prev,
                    requirement: {
                      ...prev.requirement,
                      request_date: dateValue ? dateValue.toString() : '',
                    },
                  }));
                }}
                className="mt-1"
                classNames={{
                  input: 'bg-background text-content border border-background-foreground focus:border-primary px-3 py-2 rounded-md',
                  label: 'text-content',
                }}
                isRequired
              />
            </div>
            <div>
              <label htmlFor="requested_by" className="block text-sm font-medium text-content">
                Solicitado por
              </label>
              <Input
                type="number"
                id="requested_by"
                name="requested_by"
                value={formData.requirement.requested_by !== undefined ? formData.requirement.requested_by.toString() : ''}
                onChange={handleRequirementChange}
                placeholder="Ingrese el ID del solicitante"
                className="mt-1"
                classNames={{
                  input: 'bg-background text-content border border-background-foreground focus:border-primary px-3 py-2 rounded-md',
                  label: 'text-content',
                }}
                required
              />
            </div>
            <div>
              <label htmlFor="state_id" className="block text-sm font-medium text-content">
                Estado
              </label>
              <select
                id="state_id"
                name="state_id"
                value={formData.requirement.state_id}
                onChange={handleRequirementChange}
                className="rounded-md border px-3 py-2 bg-background text-content border-background-foreground focus:border-primary"
                required
              >
                <option value={0} disabled>Seleccione un estado</option>
                {states.map((state) => (
                  <option key={state.id} value={state.id}>
                    {state.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="closing_date" className="block text-sm font-medium text-content">
                Fecha de Cierre
              </label>
              <DatePicker
                id="closing_date"
                name="closing_date"
                value={formData.requirement.closing_date ? parseDate(formData.requirement.closing_date) : null}
                onChange={(dateValue) => {
                  setFormData((prev) => ({
                    ...prev,
                    requirement: {
                      ...prev.requirement,
                      closing_date: dateValue ? dateValue.toString() : '',
                    },
                  }));
                }}
                className="mt-1"
                classNames={{
                  input: 'bg-background text-content border border-background-foreground focus:border-primary px-3 py-2 rounded-md',
                  label: 'text-content',
                }}
                isRequired={false}
              />
            </div>
          </div>
        </div>

        <Divider />

        <div className="shadow rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-medium">Artículos</h2>
            <Button
              type="button"
              onClick={addArticle}
              variant="solid"
              color="primary"
            >
              Agregar Artículo
            </Button>
          </div>

          <div className="space-y-4">
            {formData.articles.map((article, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-md font-medium">
                    Artículo {index + 1}
                  </h3>
                  <Button
                    type="button"
                    onClick={() => removeArticle(index)}
                    color="danger"
                    variant="light"
                  >
                    Eliminar
                  </Button>
                </div>
                <div className="grid grid-cols-1 gap-4">
                  <div className="grid grid-cols-6 gap-4">
                    <div>
                      <label htmlFor={`quantity-${index}`} className="block text-sm font-medium text-content">
                        Cantidad
                      </label>
                      <Input
                        type="number"
                        id={`quantity-${index}`}
                        name="quantity"
                        value={article.quantity !== undefined ? article.quantity.toString() : ''}
                        onChange={(e) => handleArticleChange(index, e)}
                        required
                        min="1"
                      />
                    </div>
                    <div>
                      <label htmlFor={`unit-${index}`} className="block text-sm font-medium text-content">
                        Unidad
                      </label>
                      <Input
                        type="text"
                        id={`unit-${index}`}
                        name="unit"
                        value={article.unit}
                        onChange={(e) => handleArticleChange(index, e)}
                        required
                      />
                    </div>
                    <div>
                      <label htmlFor={`brand-${index}`} className="block text-sm font-medium text-content">
                        Marca
                      </label>
                      <Input
                        type="text"
                        id={`brand-${index}`}
                        name="brand"
                        value={article.brand}
                        onChange={(e) => handleArticleChange(index, e)}
                        required
                      />
                    </div>
                    <div>
                      <label htmlFor={`model-${index}`} className="block text-sm font-medium text-content">
                        Modelo
                      </label>
                      <Input
                        type="text"
                        id={`model-${index}`}
                        name="model"
                        value={article.model}
                        onChange={(e) => handleArticleChange(index, e)}
                        required
                      />
                    </div>
                    <div>
                      <label htmlFor={`dimensions-${index}`} className="block text-sm font-medium text-content">
                        Dimensiones
                      </label>
                      <Input
                        type="text"
                        id={`dimensions-${index}`}
                        name="dimensions"
                        value={article.dimensions}
                        onChange={(e) => handleArticleChange(index, e)}
                        required
                      />
                    </div>
                    <div>
                      <label htmlFor={`state_id-${index}`} className="block text-sm font-medium text-content">
                        Estado
                      </label>
                      <select
                        id={`state_id-${index}`}
                        name="state_id"
                        value={article.state_id}
                        onChange={(e) => handleArticleChange(index, e)}
                        className="rounded-md border px-3 py-2 bg-background text-content border-background-foreground focus:border-primary"
                        required
                      >
                        <option value={0} disabled>Seleccione un estado</option>
                        {articleStates.map((state) => (
                          <option key={state.id} value={state.id}>
                            {state.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div>
                    <label htmlFor={`notes-${index}`} className="block text-sm font-medium text-content">
                      Notas
                    </label>
                    <textarea
                      id={`notes-${index}`}
                      name="notes"
                      value={article.notes}
                      onChange={(e) => handleArticleChange(index, e)}
                      className="rounded-md border px-3 py-2 bg-background text-content border-background-foreground focus:border-primary"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-6">
          <Button
            type="submit"
            color="primary"
            variant="solid"
            isLoading={loading}
          >
            {loading ? 'Creando...' : 'Crear Requerimiento'}
          </Button>
        </div>
      </form>
    </div>
  );
}