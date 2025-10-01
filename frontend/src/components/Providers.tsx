'use client';

import { OrganizationProvider } from '@/contexts/OrganizationContext';
import { ChatProvider } from '@/components/providers/chat-provider';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <OrganizationProvider>
      <ChatProvider>
        {children}
      </ChatProvider>
    </OrganizationProvider>
  );
}

