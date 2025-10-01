'use client';

import { OrganizationProvider } from '@/contexts/OrganizationContext';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <OrganizationProvider>
      {children}
    </OrganizationProvider>
  );
}

