'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useOrganization } from '@/contexts/OrganizationContext';

interface TerminalLine {
  type: 'command' | 'output' | 'error' | 'success';
  content: string;
}

export default function InteractiveTerminal() {
  const router = useRouter();
  const { organizations, setSelectedOrg } = useOrganization();
  const [currentCommand, setCurrentCommand] = useState('');
  const [history, setHistory] = useState<TerminalLine[]>([
    { type: 'command', content: '$ evaluate --organization "AirCanada" --round 1' },
    { type: 'output', content: '✓ Running 314 safety scenarios...' },
    { type: 'output', content: '✓ 3 LLM judges: Claude Sonnet 4.5, GPT-5, Grok-4' },
    { type: 'success', content: '→ Pass Rate: 77.9% → 94.1% → 97.4%' },
    { type: 'output', content: '' },
    { type: 'command', content: '$ --help' },
    { type: 'output', content: '' },
    { type: 'success', content: 'Available Commands:' },
    { type: 'output', content: '  --help                       Show this help message' },
    { type: 'output', content: '  create --organization "name" Create a new organization' },
    { type: 'output', content: '  list orgs                    List all organizations' },
    { type: 'output', content: '  select <slug>                Select and open organization dashboard' },
    { type: 'output', content: '  clear                        Clear terminal' },
    { type: 'output', content: '' },
  ]);
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const terminalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Auto-focus the input
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    // Auto-scroll to bottom when new lines are added
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [history]);

  const addLine = (line: TerminalLine) => {
    setHistory(prev => [...prev, line]);
  };

  const parseCommand = (cmd: string) => {
    const trimmed = cmd.trim();
    
    // Help command
    if (trimmed === '--help' || trimmed === 'help') {
      addLine({ type: 'command', content: `$ ${trimmed}` });
      addLine({ type: 'output', content: '' });
      addLine({ type: 'success', content: 'Available Commands:' });
      addLine({ type: 'output', content: '  --help                       Show this help message' });
      addLine({ type: 'output', content: '  create --organization "name" Create a new organization' });
      addLine({ type: 'output', content: '  list orgs                    List all organizations' });
      addLine({ type: 'output', content: '  select <slug>                Select and open organization dashboard' });
      addLine({ type: 'output', content: '  clear                        Clear terminal' });
      addLine({ type: 'output', content: '' });
      return;
    }

    // Clear command
    if (trimmed === 'clear') {
      setHistory([
        { type: 'output', content: 'Welcome to AI Safety Terminal. Type --help for available commands.' }
      ]);
      return;
    }

    // Create organization command
    if (trimmed.startsWith('create --organization') || trimmed.startsWith('create')) {
      addLine({ type: 'command', content: `$ ${trimmed}` });
      
      // Extract organization name from quotes
      const match = trimmed.match(/["']([^"']+)["']/);
      if (match) {
        const orgName = match[1];
        addLine({ type: 'success', content: `Creating organization: ${orgName}` });
        addLine({ type: 'output', content: 'Opening organization creation page...' });
        
        // Navigate to dashboard with create mode (you can customize this)
        setTimeout(() => {
          router.push('/dashboard?action=create');
        }, 500);
      } else {
        addLine({ type: 'error', content: 'Error: Please provide organization name in quotes' });
        addLine({ type: 'output', content: 'Usage: create --organization "Organization Name"' });
      }
      return;
    }

    // List organizations command
    if (trimmed === 'list orgs' || trimmed === 'list') {
      addLine({ type: 'command', content: `$ ${trimmed}` });
      addLine({ type: 'output', content: '' });
      
      if (organizations.length === 0) {
        addLine({ type: 'output', content: 'No organizations found.' });
        addLine({ type: 'output', content: 'Create one with: create --organization "name"' });
      } else {
        addLine({ type: 'success', content: `Found ${organizations.length} organization(s):` });
        addLine({ type: 'output', content: '' });
        organizations.forEach((org, idx) => {
          addLine({ 
            type: 'output', 
            content: `  ${idx + 1}. ${org.name}`
          });
          addLine({ 
            type: 'output', 
            content: `     slug: ${org.slug}`
          });
          if (idx < organizations.length - 1) {
            addLine({ type: 'output', content: '' });
          }
        });
        addLine({ type: 'output', content: '' });
        addLine({ type: 'output', content: 'Use "select <slug>" to open dashboard' });
      }
      return;
    }

    // Select organization command
    if (trimmed.startsWith('select ')) {
      const slug = trimmed.substring(7).trim();
      addLine({ type: 'command', content: `$ ${trimmed}` });
      
      const org = organizations.find(o => o.slug === slug);
      
      if (org) {
        addLine({ type: 'success', content: `Selected: ${org.name}` });
        addLine({ type: 'output', content: 'Opening dashboard...' });
        
        setSelectedOrg(org.id);
        setTimeout(() => {
          router.push('/dashboard');
        }, 500);
      } else {
        addLine({ type: 'error', content: `Error: Organization "${slug}" not found` });
        addLine({ type: 'output', content: 'Use "list orgs" to see available organizations' });
      }
      return;
    }

    // Unknown command
    addLine({ type: 'command', content: `$ ${trimmed}` });
    addLine({ type: 'error', content: `Unknown command: ${trimmed}` });
    addLine({ type: 'output', content: 'Type --help to see available commands' });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!currentCommand.trim()) {
      addLine({ type: 'command', content: '$' });
      setCurrentCommand('');
      return;
    }

    // Add to command history
    setCommandHistory(prev => [...prev, currentCommand]);
    setHistoryIndex(-1);

    parseCommand(currentCommand);
    setCurrentCommand('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // Navigate command history with up/down arrows
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (commandHistory.length > 0) {
        const newIndex = historyIndex === -1 
          ? commandHistory.length - 1 
          : Math.max(0, historyIndex - 1);
        setHistoryIndex(newIndex);
        setCurrentCommand(commandHistory[newIndex]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex !== -1) {
        const newIndex = historyIndex + 1;
        if (newIndex >= commandHistory.length) {
          setHistoryIndex(-1);
          setCurrentCommand('');
        } else {
          setHistoryIndex(newIndex);
          setCurrentCommand(commandHistory[newIndex]);
        }
      }
    }
  };

  const handleTerminalClick = () => {
    inputRef.current?.focus();
  };

  const getLineColor = (type: TerminalLine['type']) => {
    switch (type) {
      case 'command':
        return 'text-green-400';
      case 'success':
        return 'text-purple-400';
      case 'error':
        return 'text-red-400';
      case 'output':
      default:
        return 'text-gray-300';
    }
  };

  return (
    <div className="mt-16 mx-auto max-w-4xl">
      <div className="rounded-2xl bg-card/50 backdrop-blur-sm border border-purple-500/20 shadow-purple-glow overflow-hidden">
        {/* Terminal Header */}
        <div className="flex items-center gap-2 px-4 py-3 bg-card/80 border-b border-purple-500/20">
          <div className="flex gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <div className="w-3 h-3 rounded-full bg-green-500" />
          </div>
          <div className="flex-1 text-center">
            <span className="text-sm text-gray-400 font-mono">ai-safety-terminal</span>
          </div>
        </div>

        {/* Terminal Content */}
        <div 
          ref={terminalRef}
          onClick={handleTerminalClick}
          className="p-6 font-mono text-sm md:text-base min-h-[400px] max-h-[500px] overflow-y-auto cursor-text"
          style={{ scrollbarWidth: 'thin' }}
        >
          {/* History */}
          {history.map((line, idx) => (
            <div key={idx} className={`${getLineColor(line.type)} whitespace-pre-wrap`}>
              {line.content}
            </div>
          ))}

          {/* Input Line */}
          <form onSubmit={handleSubmit} className="flex items-center gap-2 mt-2">
            <span className="text-green-400">$</span>
            <input
              ref={inputRef}
              type="text"
              value={currentCommand}
              onChange={(e) => setCurrentCommand(e.target.value)}
              onKeyDown={handleKeyDown}
              className="flex-1 bg-transparent outline-none text-gray-100 caret-purple-400"
              placeholder="Type --help for commands..."
              autoComplete="off"
              spellCheck="false"
            />
            <span className="text-purple-400 animate-pulse">▊</span>
          </form>
        </div>
      </div>

      {/* Quick Tips */}
      <div className="mt-4 text-center text-sm text-gray-500 space-y-1">
        <p>💡 Tip: Click anywhere in the terminal to start typing</p>
        <p>⌨️ Use ↑↓ arrow keys to navigate command history</p>
      </div>
    </div>
  );
}

