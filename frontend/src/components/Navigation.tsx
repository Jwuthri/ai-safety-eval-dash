'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useOrganization } from '@/contexts/OrganizationContext';

export function Navigation() {
  const pathname = usePathname();
  const { currentOrganization } = useOrganization();

  const navItems = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/safety-story', label: 'Safety Story' },
    { href: '/taxonomy', label: 'AI Scenarios' },
    { href: '/evaluations/run', label: 'Run Evaluation' },
    { href: '/generated-scenarios', label: 'Generate Scenarios' },
  ];

  return (
    <header className="border-b border-purple-500/20 bg-card/30 backdrop-blur-sm sticky top-0 z-50">
      <div className="mx-auto max-w-7xl px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/" className="text-xl font-bold gradient-text">
              AI Safety Eval
            </Link>
            <nav className="hidden md:flex gap-6">
              {navItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`transition-colors ${
                      isActive
                        ? 'text-purple-400 font-medium'
                        : 'text-gray-400 hover:text-purple-400'
                    }`}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>
          {currentOrganization && (
            <div className="flex items-center gap-3 px-4 py-2 bg-background/50 border border-purple-500/30 rounded-lg">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              <span className="text-sm font-medium text-white">{currentOrganization.name}</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

