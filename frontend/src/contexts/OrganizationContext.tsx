'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '@/lib/api/client';

interface Organization {
  id: string;
  name: string;
  business_type_id: string;
  slug: string;
  is_active: boolean;
}

interface OrganizationContextType {
  organizations: Organization[];
  selectedOrg: string | null;
  setSelectedOrg: (orgId: string) => void;
  currentOrganization: Organization | null;
  loading: boolean;
  refreshOrganizations: () => Promise<void>;
}

const OrganizationContext = createContext<OrganizationContextType | undefined>(undefined);

export function OrganizationProvider({ children }: { children: ReactNode }) {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [selectedOrg, setSelectedOrgState] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadOrganizations() {
    try {
      const orgs = await api.getOrganizations();
      setOrganizations(orgs);
      
      // Auto-select first org if none selected
      if (!selectedOrg && orgs.length > 0) {
        const savedOrg = localStorage.getItem('selectedOrgId');
        if (savedOrg && orgs.find((o: Organization) => o.id === savedOrg)) {
          setSelectedOrgState(savedOrg);
        } else {
          setSelectedOrgState(orgs[0].id);
        }
      }
    } catch (error) {
      console.error('Failed to load organizations:', error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadOrganizations();
  }, []);

  const setSelectedOrg = (orgId: string) => {
    setSelectedOrgState(orgId);
    localStorage.setItem('selectedOrgId', orgId);
  };

  const currentOrganization = organizations.find(org => org.id === selectedOrg) || null;

  return (
    <OrganizationContext.Provider
      value={{
        organizations,
        selectedOrg,
        setSelectedOrg,
        currentOrganization,
        loading,
        refreshOrganizations: loadOrganizations,
      }}
    >
      {children}
    </OrganizationContext.Provider>
  );
}

export function useOrganization() {
  const context = useContext(OrganizationContext);
  if (context === undefined) {
    throw new Error('useOrganization must be used within an OrganizationProvider');
  }
  return context;
}

