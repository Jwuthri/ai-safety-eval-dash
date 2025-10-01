'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { useOrganization } from '@/contexts/OrganizationContext';

interface TaxonomyNode {
  name: string;
  count: number;
  children?: TaxonomyNode[];
  scenarios?: Array<{
    id: string;
    input_prompt: string;
    use_case: string;
  }>;
}

export default function TaxonomyPage() {
  const { currentOrganization, loading: orgLoading } = useOrganization();
  const [loading, setLoading] = useState(false);
  const [taxonomy, setTaxonomy] = useState<Record<string, TaxonomyNode>>({});
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const [expandedSubCategories, setExpandedSubCategories] = useState<Set<string>>(new Set());
  const [selectedScenario, setSelectedScenario] = useState<any>(null);

  useEffect(() => {
    if (currentOrganization) {
      loadTaxonomy();
    }
  }, [currentOrganization]);

  async function loadTaxonomy() {
    if (!currentOrganization) return;
    
    try {
      // Fetch scenarios and build taxonomy tree
      const response = await fetch(`http://localhost:8000/api/v1/scenarios?business_type_id=${currentOrganization.business_type_id}`);
      const scenarios = await response.json();

      // Build hierarchical structure
      const tree: Record<string, TaxonomyNode> = {};
      
      scenarios.forEach((scenario: any) => {
        const category = scenario.category || 'Uncategorized';
        const subCategory = scenario.sub_category || 'General';
        
        if (!tree[category]) {
          tree[category] = {
            name: category,
            count: 0,
            children: {}
          };
        }
        
        if (!tree[category].children) tree[category].children = {};
        const subCatKey = subCategory;
        
        if (!tree[category].children[subCatKey]) {
          tree[category].children[subCatKey] = {
            name: subCategory,
            count: 0,
            scenarios: []
          };
        }
        
        tree[category].count++;
        tree[category].children[subCatKey].count++;
        tree[category].children[subCatKey].scenarios!.push({
          id: scenario.id,
          input_prompt: scenario.input_prompt,
          use_case: scenario.use_case
        });
      });

      setTaxonomy(tree);
    } catch (error) {
      console.error('Failed to load taxonomy:', error);
    } finally {
      setLoading(false);
    }
  }

  function toggleCategory(category: string) {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  }

  function toggleSubCategory(subCategory: string) {
    const newExpanded = new Set(expandedSubCategories);
    if (newExpanded.has(subCategory)) {
      newExpanded.delete(subCategory);
    } else {
      newExpanded.add(subCategory);
    }
    setExpandedSubCategories(newExpanded);
  }

  if (orgLoading || loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading taxonomy...</p>
        </div>
      </div>
    );
  }

  if (!currentOrganization) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🏢</div>
          <h3 className="text-2xl font-bold text-white mb-2">No Organization Selected</h3>
          <p className="text-gray-400 mb-6">Please select an organization from the dashboard first.</p>
          <Link
            href="/dashboard"
            className="inline-block px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:from-purple-700 hover:to-blue-700 transition-all font-semibold"
          >
            Go to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const totalScenarios = Object.values(taxonomy).reduce((sum, cat) => sum + cat.count, 0);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-purple-500/20 bg-card/30 backdrop-blur-sm sticky top-0 z-50">
        <div className="mx-auto max-w-7xl px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-8">
              <Link href="/" className="text-xl font-bold gradient-text">
                AI Safety Eval
              </Link>
              <nav className="hidden md:flex gap-6">
                <Link href="/dashboard" className="text-gray-400 hover:text-purple-400 transition-colors">
                  Dashboard
                </Link>
                <Link href="/evaluations/run" className="text-gray-400 hover:text-purple-400 transition-colors">
                  Run Evaluation
                </Link>
                <Link href="/taxonomy" className="text-purple-400 font-medium">
                  Taxonomy
                </Link>
              </nav>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-400">{currentOrganization.name}</span>
              <div className="w-2 h-2 rounded-full bg-green-500" />
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-2">Test Taxonomy</h1>
          <p className="text-gray-400">
            Explore {totalScenarios} test scenarios across {Object.keys(taxonomy).length} categories
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Taxonomy Tree */}
          <div className="lg:col-span-2">
            <div className="p-6 rounded-2xl bg-card/30 backdrop-blur-sm border border-purple-500/20">
              <h2 className="text-xl font-semibold text-white mb-6">📊 Category Breakdown</h2>
              
              <div className="space-y-2">
                {Object.entries(taxonomy).map(([categoryKey, category]) => (
                  <div key={categoryKey}>
                    {/* Category */}
                    <motion.button
                      onClick={() => toggleCategory(categoryKey)}
                      className="w-full flex items-center justify-between p-4 rounded-xl bg-background/50 hover:bg-background/70 transition-all text-left"
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                    >
                      <div className="flex items-center gap-3">
                        <motion.div
                          animate={{ rotate: expandedCategories.has(categoryKey) ? 90 : 0 }}
                          transition={{ duration: 0.2 }}
                        >
                          <svg className="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </motion.div>
                        <span className="text-white font-medium">{category.name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-400">{category.count} tests</span>
                        <div className="w-2 h-2 rounded-full bg-purple-500" />
                      </div>
                    </motion.button>

                    {/* Sub-categories */}
                    <AnimatePresence>
                      {expandedCategories.has(categoryKey) && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.2 }}
                          className="overflow-hidden ml-8 mt-2 space-y-2"
                        >
                          {category.children && Object.entries(category.children).map(([subCatKey, subCategory]) => (
                            <div key={subCatKey}>
                              {/* Sub-category */}
                              <motion.button
                                onClick={() => toggleSubCategory(`${categoryKey}-${subCatKey}`)}
                                className="w-full flex items-center justify-between p-3 rounded-lg bg-card/50 hover:bg-card/70 transition-all text-left"
                                whileHover={{ scale: 1.01 }}
                                whileTap={{ scale: 0.99 }}
                              >
                                <div className="flex items-center gap-3">
                                  <motion.div
                                    animate={{ rotate: expandedSubCategories.has(`${categoryKey}-${subCatKey}`) ? 90 : 0 }}
                                    transition={{ duration: 0.2 }}
                                  >
                                    <svg className="w-4 h-4 text-purple-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                    </svg>
                                  </motion.div>
                                  <span className="text-gray-300 text-sm">{subCategory.name}</span>
                                </div>
                                <span className="text-xs text-gray-500">{subCategory.count} tests</span>
                              </motion.button>

                              {/* Scenarios */}
                              <AnimatePresence>
                                {expandedSubCategories.has(`${categoryKey}-${subCatKey}`) && (
                                  <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: 'auto', opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    transition={{ duration: 0.2 }}
                                    className="overflow-hidden ml-6 mt-2 space-y-1"
                                  >
                                    {subCategory.scenarios?.map((scenario) => (
                                      <button
                                        key={scenario.id}
                                        onClick={() => setSelectedScenario(scenario)}
                                        className="w-full text-left p-2 rounded hover:bg-purple-500/10 transition-all text-xs text-gray-400 hover:text-purple-300 truncate"
                                      >
                                        • {scenario.input_prompt}
                                      </button>
                                    ))}
                                  </motion.div>
                                )}
                              </AnimatePresence>
                            </div>
                          ))}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Details Panel */}
          <div className="lg:col-span-1">
            <div className="p-6 rounded-2xl bg-card/30 backdrop-blur-sm border border-purple-500/20 sticky top-24">
              <h2 className="text-xl font-semibold text-white mb-6">📝 Scenario Details</h2>
              
              {selectedScenario ? (
                <div className="space-y-4">
                  <div>
                    <label className="text-xs text-gray-500 uppercase tracking-wider">Scenario ID</label>
                    <p className="text-sm text-gray-300 font-mono mt-1">{selectedScenario.id.slice(0, 8)}...</p>
                  </div>
                  
                  <div>
                    <label className="text-xs text-gray-500 uppercase tracking-wider">Use Case</label>
                    <p className="text-sm text-purple-300 mt-1">{selectedScenario.use_case}</p>
                  </div>
                  
                  <div>
                    <label className="text-xs text-gray-500 uppercase tracking-wider">Test Prompt</label>
                    <p className="text-sm text-white mt-1 leading-relaxed">
                      {selectedScenario.input_prompt}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <svg className="w-12 h-12 mx-auto mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="text-sm">Select a scenario to view details</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

