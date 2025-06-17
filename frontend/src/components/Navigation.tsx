'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Navbar,
  NavbarBrand,
  NavbarContent,
  NavbarItem,
  Button,
} from '@heroui/react';
import {
  HomeIcon,
  DocumentTextIcon,
  UserIcon,
  Bars3Icon,
  XMarkIcon,
  ArchiveBoxIcon,
  BuildingOfficeIcon,
  BriefcaseIcon,
} from '@heroicons/react/24/outline';
import ThemeToggle from './ThemeToggle';

const navigationItems = [
  { name: 'Home', href: '/', icon: HomeIcon },
  { name: 'Usuarios', href: '/users', icon: UserIcon },
  { name: 'Requerimientos', href: '/requirements', icon: DocumentTextIcon },
  { name: 'Clientes', href: '/clients', icon: BuildingOfficeIcon },
  { name: 'Proveedores', href: '/suppliers', icon: ArchiveBoxIcon },
  { name: 'Proyectos', href: '/projects', icon: BriefcaseIcon },
];

export default function Navigation() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const pathname = usePathname();

  return (
    <Navbar 
      className="bg-background border-b border-background-foreground"
      maxWidth="full"
    >
      <NavbarBrand>
        <Link href="/" className="text-content font-bold">
          Requirements System
        </Link>
      </NavbarBrand>

      <NavbarContent className="hidden sm:flex gap-4" justify="center">
        {navigationItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <NavbarItem key={item.name}>
              <Link
                href={item.href}
                className={`flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${
                  isActive
                    ? 'text-primary bg-primary-50'
                    : 'text-content-foreground hover:bg-background-foreground'
                }`}
              >
                <item.icon className="w-5 h-5" />
                {item.name}
              </Link>
            </NavbarItem>
          );
        })}
      </NavbarContent>

      <NavbarContent justify="end">
        <NavbarItem>
          <ThemeToggle />
        </NavbarItem>
      </NavbarContent>

      {/* Mobile menu button */}
      <div className="sm:hidden">
        <Button
          isIconOnly
          variant="light"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="text-content-foreground"
        >
          {isMenuOpen ? (
            <XMarkIcon className="w-6 h-6" />
          ) : (
            <Bars3Icon className="w-6 h-6" />
          )}
        </Button>
      </div>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div className="sm:hidden absolute top-16 left-0 right-0 bg-background border-b border-background-foreground">
          <div className="px-2 pt-2 pb-3 space-y-1">
            {navigationItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${
                    isActive
                      ? 'text-primary bg-primary-50'
                      : 'text-content-foreground hover:bg-background-foreground'
                  }`}
                  onClick={() => setIsMenuOpen(false)}
                >
                  <item.icon className="w-5 h-5" />
                  {item.name}
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </Navbar>
  );
} 