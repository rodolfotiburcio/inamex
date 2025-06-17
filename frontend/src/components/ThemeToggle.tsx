'use client';

import { Button } from '@heroui/react';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';
import { useTheme } from './ThemeProvider';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <Button
      isIconOnly
      variant="light"
      onClick={toggleTheme}
      className="text-content-foreground hover:text-content"
    >
      {theme === 'light' ? (
        <MoonIcon className="w-5 h-5" />
      ) : (
        <SunIcon className="w-5 h-5" />
      )}
    </Button>
  );
} 