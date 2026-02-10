
import React, { useState, useEffect, useCallback } from 'react';
import Layout from './components/Layout';
import { TabType, MorphologicalScheme, RootNodeData } from './types';
import { TreeView } from './components/TreeView';
import { 
  FileText, 
  ArrowRight, 
  Plus, 
  Search, 
  History, 
  Settings2, 
  ChevronRight,
  Database,
  BrainCircuit,
  Wand2,
  SearchCheck,
  Trash2,
  AlertCircle,
  Save,
  Loader2
} from 'lucide-react';

const API_BASE = 'http://localhost:8000/api';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>(TabType.DASHBOARD);
  const [roots, setRoots] = useState<RootNodeData[]>([]);
  const [schemes, setSchemes] = useState<MorphologicalScheme[]>([]);
  const [treeVisual, setTreeVisual] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // Form States
  const [genRoot, setGenRoot] = useState("");
  const [genSchemeId, setGenSchemeId] = useState("");
  const [genResult, setGenResult] = useState<string | null>(null);
  const [valWord, setValWord] = useState("");
  const [valRoot, setValRoot] = useState("");
  const [valResult, setValResult] = useState<{ isValid: boolean; scheme?: string } | null>(null);
  const [newScheme, setNewScheme] = useState({ id: '', pattern: '', rule: '' });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [rRes, sRes, vRes] = await Promise.all([
        fetch(`${API_BASE}/roots`),
        fetch(`${API_BASE}/schemes`), 
        fetch(`${API_BASE}/roots/visual`)
      ]);

      // Normalise backend data so UI always has derivedWords[]
      const rawRoots = await rRes.json();
      const normalizedRoots: RootNodeData[] = rawRoots.map((r: any) => ({
        root: r.root,
        derivedWords: r.derivedWords || r.derived_words || [],
      }));

      setRoots(normalizedRoots);
      setSchemes(await sRes.json());
      setTreeVisual(await vRes.json());
    } catch (e) {
      console.error("Backend connection failed", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleAddRoot = async (val: string) => {
    if (val.trim().length !== 3) return;
    setLoading(true);
    await fetch(`${API_BASE}/roots?root=${encodeURIComponent(val)}`, { method: 'POST' });
    fetchData();
  };

  const handleAddScheme = async () => {
    if (!newScheme.id || !newScheme.pattern) return;
    setLoading(true);
    await fetch(`${API_BASE}/schemes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...newScheme, transformationRule: newScheme.rule })
    });
    setNewScheme({ id: '', pattern: '', rule: '' });
    fetchData();
  };

  const handleGenerate = async () => {
    if (!genRoot || !genSchemeId) return;
    setLoading(true);
    const res = await fetch(`${API_BASE}/generate?root=${encodeURIComponent(genRoot)}&scheme_id=${encodeURIComponent(genSchemeId)}`, { method: 'POST' });
    const data = await res.json();
    setGenResult(data.word);
    fetchData(); // Refresh history
  };

  const handleValidate = async () => {
    if (!valWord || !valRoot) return;
    setLoading(true);
    const res = await fetch(`${API_BASE}/validate?word=${encodeURIComponent(valWord)}&root_str=${encodeURIComponent(valRoot)}`, { method: 'POST' });
    const data = await res.json();
    setValResult(data);
    fetchData(); // Refresh history
  };

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      
      {activeTab === TabType.DASHBOARD && (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-emerald-100 p-3 rounded-xl text-emerald-600"><Database className="w-6 h-6" /></div>
                {loading && <Loader2 className="w-4 h-4 animate-spin text-slate-300" />}
              </div>
              <h3 className="text-3xl font-bold text-slate-800">{roots.length}</h3>
              <p className="text-slate-500 text-sm mt-1">Racines (Python AVL)</p>
            </div>
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-indigo-100 p-3 rounded-xl text-indigo-600"><Settings2 className="w-6 h-6" /></div>
              </div>
              <h3 className="text-3xl font-bold text-slate-800">{schemes.length}</h3>
              <p className="text-slate-500 text-sm mt-1">Schèmes (Python Hash)</p>
            </div>
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-amber-100 p-3 rounded-xl text-amber-600"><BrainCircuit className="w-6 h-6" /></div>
              </div>
              <h3 className="text-3xl font-bold text-slate-800">Dynamic</h3>
              <p className="text-slate-500 text-sm mt-1">Python API Connected</p>
            </div>
          </div>

          <div className="bg-blue-600 rounded-2xl p-8 text-white shadow-xl shadow-blue-200 flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="space-y-2">
              <h2 className="text-2xl font-bold">Moteur Morphologique Backend</h2>
              <p className="opacity-90 max-w-lg">Le serveur Python gère désormais les algorithmes complexes, assurant une validation exacte et une dérivation instantanée.</p>
            </div>
            <button 
              onClick={() => setActiveTab(TabType.VALIDATOR)}
              className="bg-white text-blue-600 px-6 py-3 rounded-xl font-bold hover:bg-slate-50 transition-colors shrink-0"
            >
              Tester la Validation
            </button>
          </div>
        </div>
      )}

      {activeTab === TabType.ROOTS && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-4">
             <div>
                <h3 className="text-lg font-bold text-slate-800">Gestion des Racines</h3>
                <p className="text-sm text-slate-500">Ajout dynamique dans l'arbre AVL Python.</p>
             </div>
             <div className="flex gap-2">
                <input 
                  type="text" 
                  id="rootInput"
                  placeholder="Ex: كتب"
                  className="bg-slate-50 border border-slate-200 px-4 py-2 rounded-lg text-right font-arabic text-lg w-40 outline-none focus:ring-2 focus:ring-blue-500"
                  maxLength={3}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleAddRoot(e.currentTarget.value);
                      e.currentTarget.value = "";
                    }
                  }}
                />
                <button 
                  onClick={() => {
                    const el = document.getElementById('rootInput') as HTMLInputElement;
                    handleAddRoot(el.value);
                    el.value = "";
                  }}
                  className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Plus className="w-6 h-6" />
                </button>
             </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <BrainCircuit className="w-4 h-4 text-blue-500" />
                <span className="text-xs font-bold text-slate-600 uppercase">Structure AVL (Server-Side)</span>
              </div>
              {loading && <Loader2 className="w-4 h-4 animate-spin text-blue-500" />}
            </div>
            <div className="p-8 min-h-[400px]">
               <TreeView data={treeVisual} />
            </div>
          </div>
        </div>
      )}

      {activeTab === TabType.SCHEMES && (
        <div className="space-y-6">
           <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
              <h3 className="text-lg font-bold text-slate-800 mb-4">Nouveau Schème (Hash Bucket)</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                 <input 
                   placeholder="ID (ex: اسم_آلة)" 
                   className="bg-slate-50 p-3 rounded-xl border border-slate-200"
                   value={newScheme.id}
                   onChange={e => setNewScheme({...newScheme, id: e.target.value})}
                 />
                 <input 
                   placeholder="Patron (ex: مِفْعَال)" 
                   className="bg-slate-50 p-3 rounded-xl border border-slate-200 font-arabic text-xl text-right"
                   value={newScheme.pattern}
                   onChange={e => setNewScheme({...newScheme, pattern: e.target.value})}
                 />
                 <input 
                   placeholder="Usage" 
                   className="bg-slate-50 p-3 rounded-xl border border-slate-200"
                   value={newScheme.rule}
                   onChange={e => setNewScheme({...newScheme, rule: e.target.value})}
                 />
               </div>
              <button 
                onClick={handleAddScheme}
                className="w-full bg-slate-800 text-white py-3 rounded-xl font-bold flex items-center justify-center gap-2"
              >
                <Save className="w-4 h-4" /> {schemes.some(s => s.id === newScheme.id) ? 'Mettre à jour le Schème' : 'Sauvegarder dans la Hash Table'}
              </button>
           </div>

           <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 overflow-x-auto">
              <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center justify-between">
                Schèmes Actuels
                {loading && <Loader2 className="w-4 h-4 animate-spin text-slate-400" />}
              </h3>
              <table className="w-full text-left">
                 <thead className="bg-slate-50 text-[10px] font-bold text-slate-400 uppercase">
                    <tr>
                       <th className="px-4 py-3">ID</th>
                       <th className="px-4 py-3">Patron</th>
                       <th className="px-4 py-3">Règle</th>
                    </tr>
                 </thead>
                 <tbody className="divide-y divide-slate-100">
                    {schemes.map(s => (
                       <tr
                         key={s.id}
                         className="hover:bg-slate-50 transition-colors cursor-pointer"
                         onClick={() => setNewScheme({ id: s.id, pattern: s.pattern, rule: s.transformationRule })}
                       >
                          <td className="px-4 py-4 font-mono font-bold text-blue-600">{s.id}</td>
                          <td className="px-4 py-4 font-arabic text-xl">{s.pattern}</td>
                          <td className="px-4 py-4 text-slate-500 text-sm">{s.transformationRule}</td>
                       </tr>
                    ))}
                 </tbody>
              </table>
           </div>
        </div>
      )}

      {activeTab === TabType.GENERATOR && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
           <div className="space-y-6">
              <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
                <h3 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2"><Wand2 className="w-6 h-6 text-blue-500" /> Générateur</h3>
                <div className="space-y-4">
                  <select className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 font-arabic text-lg text-right outline-none" value={genRoot} onChange={e => setGenRoot(e.target.value)}>
                    <option value="">-- Racine --</option>
                    {roots.map(r => <option key={r.root} value={r.root}>{r.root}</option>)}
                  </select>
                  <select className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 font-arabic text-lg text-right outline-none" value={genSchemeId} onChange={e => setGenSchemeId(e.target.value)}>
                    <option value="">-- Schème --</option>
                    {schemes.map(s => <option key={s.id} value={s.id}>{s.id} ({s.pattern})</option>)}
                  </select>
                  <button onClick={handleGenerate} disabled={!genRoot || !genSchemeId || loading} className="w-full bg-blue-600 text-white font-bold py-4 rounded-xl shadow-lg hover:bg-blue-700 disabled:opacity-50">
                    {loading ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : 'Générer'}
                  </button>
                </div>
              </div>
              {genResult && (
                <div className="bg-emerald-600 text-white p-8 rounded-2xl shadow-xl flex items-center justify-between animate-in zoom-in-95">
                  <div>
                    <span className="text-[10px] font-bold uppercase opacity-80">Dérivation Réussie</span>
                    <h2 className="text-5xl font-arabic font-bold mt-1">{genResult}</h2>
                  </div>
                  <BrainCircuit className="w-12 h-12 opacity-30" />
                </div>
              )}
           </div>
           
           <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col h-full">
             <h4 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
               <History className="w-4 h-4 text-slate-400" /> Générateur
             </h4>

             <div className="flex-1 overflow-y-auto space-y-3">
               
               {roots
                 .filter(r => (r.derivedWords?.length || 0) > 0)
                 .map(r => (
                   <div key={r.root} className="p-3 bg-slate-50 rounded-xl border border-slate-100">

                     <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">
                       {r.root}
                     </p>

                     <div className="flex flex-wrap gap-1">
                       {(r.derivedWords || []).map((dw, i) => (
                         <span
                           key={i}
                           className="bg-white border border-slate-200 text-blue-600 px-2 py-1 rounded-md text-sm font-arabic"
                         >
                           {dw.word}
                         </span>
                       ))}
                     </div>

                   </div>
               ))}

               {roots.every(r => (r.derivedWords?.length || 0) === 0) && (
                 <div className="text-center py-12 text-slate-400">
                   Aucun mot généré pour le moment.
                 </div>
               )}

             </div>
           </div>
        </div>
      )}

      {activeTab === TabType.VALIDATOR && (
        <div className="max-w-2xl mx-auto space-y-6">
           <div className="bg-white p-8 rounded-2xl shadow-md border border-slate-200">
              <div className="text-center mb-8">
                <SearchCheck className="w-12 h-12 text-blue-500 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-slate-800">Validation Algorithmique</h3>
                <p className="text-slate-400 text-sm mt-1">Normalisation et comparaison via API Python</p>
              </div>
              <div className="space-y-6">
                <div className="flex gap-4">
                  <div className="flex-1">
                    <label className="block text-xs font-bold text-slate-500 mb-2">Mot à valider</label>
                    <input className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-4 text-right font-arabic text-2xl outline-none" value={valWord} onChange={e => setValWord(e.target.value)} placeholder="Ex: مكتوب" />
                  </div>
                  <div className="w-32">
                    <label className="block text-xs font-bold text-slate-500 mb-2">Racine</label>
                    <input className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-4 text-center font-arabic text-2xl outline-none" value={valRoot} onChange={e => setValRoot(e.target.value)} maxLength={3} placeholder="كتب" />
                  </div>
                </div>
                <button onClick={handleValidate} disabled={loading} className="w-full py-4 bg-slate-800 text-white rounded-xl font-bold hover:bg-slate-900 transition-all flex items-center justify-center gap-2">
                   {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Analyser la structure'}
                </button>
              </div>
           </div>

           {valResult && (
             <div className={`p-6 rounded-2xl border flex items-center gap-4 animate-in slide-in-from-top-4 ${valResult.isValid ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-red-50 border-red-200 text-red-800'}`}>
                {valResult.isValid ? <SearchCheck className="w-8 h-8" /> : <AlertCircle className="w-8 h-8" />}
                <div>
                   <h4 className="font-bold">{valResult.isValid ? 'Validation Réussie' : 'Validation Échouée'}</h4>
                   <p className="text-sm opacity-80">{valResult.isValid ? `Mot reconnu comme pattern "${valResult.scheme}".` : 'Aucun schème correspondant trouvé après normalisation.'}</p>
                </div>
             </div>
           )}
        </div>
      )}

    </Layout>
  );
};

export default App;