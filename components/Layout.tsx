
import React from 'react';
import { TabType } from '../types';
import { LayoutDashboard, TreePine, TableProperties, Wand2, SearchCheck, GraduationCap } from 'lucide-react';

interface LayoutProps {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ activeTab, setActiveTab, children }) => {
  const menuItems = [
    { id: TabType.DASHBOARD, label: 'Tableau de bord', icon: <LayoutDashboard className="w-5 h-5" /> },
    { id: TabType.ROOTS, label: 'Gestion des Racines', icon: <TreePine className="w-5 h-5" /> },
    { id: TabType.SCHEMES, label: 'Schèmes (Hachage)', icon: <TableProperties className="w-5 h-5" /> },
    { id: TabType.GENERATOR, label: 'Générateur', icon: <Wand2 className="w-5 h-5" /> },
    { id: TabType.VALIDATOR, label: 'Validation', icon: <SearchCheck className="w-5 h-5" /> },
  ];

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col shadow-xl z-20">
        <div className="p-6 border-b border-slate-800 flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-lg">
             <GraduationCap className="text-white w-6 h-6" />
          </div>
          <div>
            <h1 className="font-bold text-lg tracking-tight">ISI Project</h1>
            <p className="text-xs text-slate-400">Algorithmique 2026</p>
          </div>
        </div>
        
        <nav className="flex-1 py-4 px-3 space-y-1">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                activeTab === item.id 
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20' 
                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`}
            >
              {item.icon}
              <span className="font-medium">{item.label}</span>
            </button>
          ))}
        </nav>
        
        <div className="p-6 border-t border-slate-800 text-xs text-slate-500">
          <p>Enseignants :</p>
          <p>N. Ben Hariz, S. Bahroun</p>
          <p className="mt-2 opacity-50">© 2025 GLSI 1ING</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 shadow-sm">
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-800">
              {menuItems.find(i => i.id === activeTab)?.label}
            </h2>
          </div>
          <div className="flex items-center gap-4 text-sm text-slate-500 bg-slate-100 px-4 py-1.5 rounded-full border border-slate-200">
             <span className="font-semibold text-slate-700">Mini projet :</span> 
             <span>Moteur Morphologique Arabe</span>
          </div>
        </header>

        <section className="flex-1 overflow-y-auto p-8 scroll-smooth">
          <div className="max-w-6xl mx-auto">
            {children}
          </div>
        </section>
      </main>
    </div>
  );
};

export default Layout;
