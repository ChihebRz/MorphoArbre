
import React, { useState, useEffect, useCallback } from 'react';
import Layout from './components/Layout';
import { TabType, MorphologicalScheme, RootNodeData, VerbTypeInfo } from './types';
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
  Loader2,
  BookOpen
} from 'lucide-react';

const API_BASE = 'http://localhost:8000/api';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>(TabType.DASHBOARD);
  const [roots, setRoots] = useState<RootNodeData[]>([]);
  const [schemes, setSchemes] = useState<MorphologicalScheme[]>([]);
  const [verbTypes, setVerbTypes] = useState<VerbTypeInfo[]>([]);
  const [treeVisual, setTreeVisual] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [selectedRoot, setSelectedRoot] = useState<RootNodeData | null>(null);

  // Form States
  const [genRoot, setGenRoot] = useState("");
  const [genSchemeId, setGenSchemeId] = useState("");
  const [genResult, setGenResult] = useState<any>(null);
  const [valWord, setValWord] = useState("");
  const [valRoot, setValRoot] = useState("");
  const [valResult, setValResult] = useState<any>(null);
  const [historyRoot, setHistoryRoot] = useState("");
  const [historyByRoot, setHistoryByRoot] = useState<RootNodeData | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [newScheme, setNewScheme] = useState({ id: '', pattern: '', rule: '' });
  const [editingSchemeId, setEditingSchemeId] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [rRes, sRes, vRes, verbRes] = await Promise.all([
        fetch(`${API_BASE}/roots`),
        fetch(`${API_BASE}/schemes`), 
        fetch(`${API_BASE}/roots/visual`),
        fetch(`${API_BASE}/verb-types`)
      ]);

      // Normalise backend data so UI always has derivedWords[]
      const rawRoots = await rRes.json();
      const normalizedRoots: RootNodeData[] = rawRoots.map((r: any) => ({
        root: r.root,
        derivedWords: (r.derivedWords || r.derived_words || []).map((dw: any) => ({
          word: dw.word,
          frequency: dw.frequency,
          timestamp: dw.timestamp,
          scheme_id: dw.scheme_id,
          pattern: dw.pattern
        })),
        verb_type: r.verb_type
      }));

      setRoots(normalizedRoots);
      setSchemes(await sRes.json());
      setTreeVisual(await vRes.json());
      setVerbTypes(await verbRes.json());
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

  const handleSaveScheme = async () => {
    if (!newScheme.id || !newScheme.pattern) return;
    setLoading(true);
    const isEditing = !!editingSchemeId;
    await fetch(isEditing ? `${API_BASE}/schemes/${encodeURIComponent(editingSchemeId)}` : `${API_BASE}/schemes`, {
      method: isEditing ? 'PUT' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...newScheme, transformationRule: newScheme.rule })
    });
    setNewScheme({ id: '', pattern: '', rule: '' });
    setEditingSchemeId(null);
    fetchData();
  };

  const handleEditScheme = (scheme: MorphologicalScheme) => {
    setEditingSchemeId(scheme.id);
    setNewScheme({
      id: scheme.id,
      pattern: scheme.pattern,
      rule: scheme.transformationRule
    });
  };

  const handleDeleteScheme = async (id: string) => {
    setLoading(true);
    await fetch(`${API_BASE}/schemes/${encodeURIComponent(id)}`, { method: 'DELETE' });
    if (editingSchemeId === id) {
      setEditingSchemeId(null);
      setNewScheme({ id: '', pattern: '', rule: '' });
    }
    fetchData();
  };

  const handleGenerate = async () => {
    if (!genRoot || !genSchemeId) return;
    setLoading(true);
    const res = await fetch(`${API_BASE}/generate?root=${encodeURIComponent(genRoot)}&scheme_id=${encodeURIComponent(genSchemeId)}`, { method: 'POST' });
    const data = await res.json();
    setGenResult(data);
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

  const handleHistoryByRoot = async () => {
    if (!historyRoot || historyRoot.trim().length !== 3) return;
    setHistoryLoading(true);
    try {
      const res = await fetch(`${API_BASE}/roots/${encodeURIComponent(historyRoot.trim())}`);
      if (!res.ok) {
        setHistoryByRoot(null);
        return;
      }
      const data = await res.json();
      setHistoryByRoot({
        root: data.root,
        derivedWords: (data.derivedWords || data.derived_words || []).map((dw: any) => ({
          word: dw.word,
          frequency: dw.frequency,
          timestamp: dw.timestamp,
          scheme_id: dw.scheme_id,
          pattern: dw.pattern
        })),
        verb_type: data.verb_type
      });
    } finally {
      setHistoryLoading(false);
    }
  };

  const getVerbTypeInfo = (type: string) => {
    return verbTypes.find(v => v.type === type);
  };

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      
      {activeTab === TabType.DASHBOARD && (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4" dir="rtl">
          <div className="flex gap-6">
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between h-80 flex-1">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="bg-emerald-100 p-3 rounded-xl text-emerald-600"><Database className="w-6 h-6" /></div>
                  {loading && <Loader2 className="w-4 h-4 animate-spin text-slate-300" />}
                </div>
                <h3 className="text-4xl font-bold text-slate-800">{roots.length}</h3>
                <p className="text-slate-500 text-lg mt-2">الجذور (AVL Python)</p>
              </div>
              <button 
                onClick={() => setActiveTab(TabType.ROOTS)}
                className="bg-white/30 text-emerald-700 px-6 py-3 rounded-xl font-bold hover:bg-white/40 transition-colors w-full backdrop-blur-md border border-white/50"
              >
                الذهاب إلى الصفحة ←
              </button>
            </div>
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between h-80 flex-1">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="bg-indigo-100 p-3 rounded-xl text-indigo-600"><Settings2 className="w-6 h-6" /></div>
                </div>
                <h3 className="text-4xl font-bold text-slate-800">{schemes.length}</h3>
                <p className="text-slate-500 text-lg mt-2">الأوزان (Hash Python)</p>
              </div>
              <button 
                onClick={() => setActiveTab(TabType.SCHEMES)}
                className="bg-white/30 text-indigo-700 px-6 py-3 rounded-xl font-bold hover:bg-white/40 transition-colors w-full backdrop-blur-md border border-white/50"
              >
                الذهاب إلى الصفحة ←
              </button>
            </div>
          </div>

          <div className="flex gap-6">
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between h-80 flex-1">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="bg-blue-100 p-3 rounded-xl text-blue-600"><Wand2 className="w-6 h-6" /></div>
                </div>
                <h3 className="text-2xl font-bold text-slate-800">المولد</h3>
                <p className="text-slate-500 text-lg mt-2">توليد الكلمات (Générateur)</p>
              </div>
              <button 
                onClick={() => setActiveTab(TabType.GENERATOR)}
                className="bg-white/30 text-blue-700 px-6 py-3 rounded-xl font-bold hover:bg-white/40 transition-colors w-full backdrop-blur-md border border-white/50"
              >
                الذهاب إلى الصفحة ←
              </button>
            </div>
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between h-80 flex-1">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="bg-purple-100 p-3 rounded-xl text-purple-600"><SearchCheck className="w-6 h-6" /></div>
                </div>
                <h3 className="text-2xl font-bold text-slate-800">التحقق</h3>
                <p className="text-slate-500 text-lg mt-2">التحقق من الكلمات (Validation)</p>
              </div>
              <button 
                onClick={() => setActiveTab(TabType.VALIDATOR)}
                className="bg-white/30 text-purple-700 px-6 py-3 rounded-xl font-bold hover:bg-white/40 transition-colors w-full backdrop-blur-md border border-white/50"
              >
                الذهاب إلى الصفحة ←
              </button>
            </div>
          </div>
        </div>
      )}

      {activeTab === TabType.ROOTS && (
        <div className="space-y-6" dir="rtl">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-4">
             <div>
                <h3 className="text-lg font-bold text-slate-800">إدارة الجذور</h3>
                <p className="text-sm text-slate-500">إضافة ديناميكية في شجرة AVL مع الكشف التلقائي عن نوع الفعل.</p>
             </div>
             <div className="flex gap-2">
                <input 
                  type="text" 
                  id="rootInput"
                  placeholder="مثال: كتب"
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
                <span className="text-xs font-bold text-slate-600 uppercase">خادم بنية AVL</span>
              </div>
              {loading && <Loader2 className="w-4 h-4 animate-spin text-blue-500" />}
            </div>
            <div className="p-8 min-h-[400px]">
               <TreeView data={treeVisual} />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {roots.map(r => {
              const verbInfo = getVerbTypeInfo(r.verb_type || '');
              return (
                <div
                  key={r.root}
                  className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 hover:border-blue-300 cursor-pointer transition-all"
                  onClick={() => setSelectedRoot(r)}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h4 className="text-2xl font-arabic font-bold text-slate-800">{r.root}</h4>
                      <p className="text-xs text-slate-500 mt-1">نوع الفعل: {r.verb_type || 'غير معروف'}</p>
                    </div>
                    <div className="bg-blue-100 p-2 rounded-lg">
                      <BookOpen className="w-5 h-5 text-blue-600" />
                    </div>
                  </div>
                  
                  {verbInfo && (
                    <div className="bg-amber-50 border-l-4 border-amber-400 p-3 rounded mb-4">
                      <p className="text-xs font-bold text-amber-900">{verbInfo.caracteristiques}</p>
                      <p className="text-xs text-amber-700 mt-1">المثال: {verbInfo.exemple}</p>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>{(r.derivedWords?.length || 0)} منشتقات</span>
                  </div>
                </div>
              );
            })}
          </div>

          {selectedRoot && (
            <div className="bg-white p-6 rounded-2xl shadow-lg border border-blue-200 fixed bottom-6 right-6 max-w-md">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h4 className="text-xl font-arabic font-bold text-slate-800">{selectedRoot.root}</h4>
                  <p className="text-sm text-slate-600 mt-1">{selectedRoot.verb_type}</p>
                </div>
                <button
                  onClick={() => setSelectedRoot(null)}
                  className="text-slate-400 hover:text-slate-600"
                >
                  ✕
                </button>
              </div>
              <div className="space-y-3">
                <h5 className="font-bold text-slate-700">المنشتقات:</h5>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {(selectedRoot.derivedWords || []).map((dw, i) => (
                    <div key={i} className="bg-slate-50 p-2 rounded text-right">
                      <p className="font-arabic text-sm">{dw.word}</p>
                      <p className="text-xs text-slate-500">
                        {dw.frequency}x{dw.scheme_id ? ` • ${dw.scheme_id}` : ''}{dw.pattern ? ` (${dw.pattern})` : ''}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === TabType.SCHEMES && (
        <div className="space-y-6" dir="rtl">
           <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
              <h3 className="text-lg font-bold text-slate-800 mb-4">وزن صرفي جديد</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                 <input 
                   placeholder="المعرّف (مثل: اسم_آلة)" 
                   className="bg-slate-50 p-3 rounded-xl border border-slate-200"
                   value={newScheme.id}
                   onChange={e => setNewScheme({...newScheme, id: e.target.value})}
                 />
                 <input 
                   placeholder="الوزن (مثل: مِفْعَال)" 
                   className="bg-slate-50 p-3 rounded-xl border border-slate-200 font-arabic text-xl text-right"
                   value={newScheme.pattern}
                   onChange={e => setNewScheme({...newScheme, pattern: e.target.value})}
                 />
                 <input 
                   placeholder="الاستخدام" 
                   className="bg-slate-50 p-3 rounded-xl border border-slate-200"
                   value={newScheme.rule}
                   onChange={e => setNewScheme({...newScheme, rule: e.target.value})}
                 />
               </div>
              <button 
                onClick={handleSaveScheme}
                className="w-full bg-slate-800 text-white py-3 rounded-xl font-bold flex items-center justify-center gap-2"
              >
                <Save className="w-4 h-4" /> {editingSchemeId ? 'تعديل الوزن' : 'إضافة الوزن'}
              </button>
              {editingSchemeId && (
                <button
                  onClick={() => {
                    setEditingSchemeId(null);
                    setNewScheme({ id: '', pattern: '', rule: '' });
                  }}
                  className="w-full mt-2 bg-slate-100 text-slate-700 py-3 rounded-xl font-bold"
                >
                  إلغاء التعديل
                </button>
              )}
           </div>

           <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 overflow-x-auto">
              <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center justify-between">
                الأوزان الحالية
                {loading && <Loader2 className="w-4 h-4 animate-spin text-slate-400" />}
              </h3>
              <table className="w-full text-right">
                 <thead className="bg-slate-50 text-[10px] font-bold text-slate-400 uppercase">
                    <tr>
                       <th className="px-4 py-3 text-right">المعرّف</th>
                       <th className="px-4 py-3 text-right">الوزن</th>
                       <th className="px-4 py-3 text-right">القاعدة</th>
                       <th className="px-4 py-3 text-right">إجراءات</th>
                    </tr>
                 </thead>
                 <tbody className="divide-y divide-slate-100">
                    {schemes.map(s => (
                       <tr key={s.id} className="hover:bg-slate-50 transition-colors">
                          <td className="px-4 py-4 font-mono font-bold text-blue-600">{s.id}</td>
                          <td className="px-4 py-4 font-arabic text-xl">{s.pattern}</td>
                          <td className="px-4 py-4 text-slate-500 text-sm">{s.transformationRule}</td>
                          <td className="px-4 py-4">
                            <div className="flex items-center justify-end gap-2">
                              <button
                                onClick={() => handleEditScheme(s)}
                                className="px-3 py-1 text-xs rounded-md bg-blue-100 text-blue-700 hover:bg-blue-200"
                              >
                                تعديل
                              </button>
                              <button
                                onClick={() => handleDeleteScheme(s.id)}
                                className="px-3 py-1 text-xs rounded-md bg-red-100 text-red-700 hover:bg-red-200"
                              >
                                حذف
                              </button>
                            </div>
                          </td>
                       </tr>
                    ))}
                 </tbody>
              </table>
           </div>
        </div>
      )}

      {activeTab === TabType.GENERATOR && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8" dir="rtl">
           <div className="space-y-6">
              <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
                <h3 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2"><Wand2 className="w-6 h-6 text-blue-500" /> المولّد الصرفي</h3>
                <div className="space-y-4">
                  <select className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 font-arabic text-lg text-right outline-none" value={genRoot} onChange={e => setGenRoot(e.target.value)}>
                    <option value="">-- اختر جذراً --</option>
                    {roots.map(r => <option key={r.root} value={r.root}>{r.root} ({r.verb_type})</option>)}
                  </select>
                  <select className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 font-arabic text-lg text-right outline-none" value={genSchemeId} onChange={e => setGenSchemeId(e.target.value)}>
                    <option value="">-- اختر وزناً --</option>
                    {schemes.map(s => <option key={s.id} value={s.id}>{s.id} ({s.pattern})</option>)}
                  </select>
                  <button onClick={handleGenerate} disabled={!genRoot || !genSchemeId || loading} className="w-full bg-blue-600 text-white font-bold py-4 rounded-xl shadow-lg hover:bg-blue-700 disabled:opacity-50">
                    {loading ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : 'توليد الكلمة'}
                  </button>
                </div>
              </div>
              {genResult && (
                <div className="bg-emerald-600 text-white p-8 rounded-2xl shadow-xl flex items-center justify-between animate-in zoom-in-95">
                  <div>
                    <span className="text-[10px] font-bold uppercase opacity-80">توليد ناجح</span>
                    <h2 className="text-5xl font-arabic font-bold mt-1">{genResult.word}</h2>
                    <p className="text-sm opacity-90 mt-2">نوع الفعل: {genResult.verb_type}</p>
                  </div>
                  <BrainCircuit className="w-12 h-12 opacity-30" />
                </div>
              )}
           </div>
           
           <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col h-full">
             <h4 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
               <History className="w-4 h-4 text-slate-400" /> السجل
             </h4>

             <div className="flex-1 overflow-y-auto space-y-3">
               
               {roots
                 .filter(r => (r.derivedWords?.length || 0) > 0)
                 .map(r => (
                   <div key={r.root} className="p-3 bg-slate-50 rounded-xl border border-slate-100">

                     <p className="text-[10px] font-bold text-slate-400 uppercase mb-1 text-right">
                       {r.root} ({r.verb_type})
                     </p>

                     <div className="flex flex-wrap gap-1 justify-end">
                       {(r.derivedWords || []).map((dw, i) => (
                         <span
                           key={i}
                           className="bg-white border border-slate-200 text-blue-600 px-2 py-1 rounded-md text-sm font-arabic"
                         >
                           {dw.word} ({dw.scheme_id || dw.pattern || 'غير معروف'})
                         </span>
                       ))}
                     </div>

                   </div>
               ))}

               {roots.every(r => (r.derivedWords?.length || 0) === 0) && (
                 <div className="text-center py-12 text-slate-400">
                   لا توجد كلمات مولدة حتى الآن.
                 </div>
               )}

             </div>
           </div>
        </div>
      )}

      {activeTab === TabType.VALIDATOR && (
        <div className="max-w-3xl mx-auto space-y-6" dir="rtl">
           <div className="bg-white p-8 rounded-2xl shadow-md border border-slate-200">
              <div className="text-center mb-6">
                <History className="w-10 h-10 text-indigo-500 mx-auto mb-3" />
                <h3 className="text-xl font-bold text-slate-800">سجل الجذر</h3>
                <p className="text-slate-400 text-sm mt-1">أدخل الجذر لإرجاع كل الكلمات المولدة المخزنة في التاريخ</p>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-500 mb-2 text-right">الجذر</label>
                  <input
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-4 text-center font-arabic text-2xl outline-none"
                    value={historyRoot}
                    onChange={e => setHistoryRoot(e.target.value)}
                    onKeyDown={e => {
                      if (e.key === 'Enter') {
                        handleHistoryByRoot();
                      }
                    }}
                    maxLength={3}
                    placeholder="مثال: كتب"
                  />
                </div>
                <button
                  onClick={handleHistoryByRoot}
                  disabled={historyLoading}
                  className="w-full py-4 bg-slate-800 text-white rounded-xl font-bold hover:bg-slate-900 transition-all flex items-center justify-center gap-2 shadow-sm"
                >
                  {historyLoading && <Loader2 className="w-5 h-5 animate-spin" />}
                  <span>إظهار كل الكلمات المخزنة</span>
                </button>
              </div>

              {historyByRoot && (
                <div className="mt-6 border border-slate-200 rounded-xl p-4 bg-slate-50">
                  <p className="text-sm text-slate-600 text-right mb-3">
                    الجذر: <strong>{historyByRoot.root}</strong> • النوع: <strong>{historyByRoot.verb_type || 'غير معروف'}</strong>
                  </p>
                  <div className="flex flex-wrap gap-2 justify-end">
                    {(historyByRoot.derivedWords || []).length > 0 ? (
                      historyByRoot.derivedWords.map((dw, i) => (
                        <span key={i} className="bg-white border border-slate-200 text-slate-700 px-3 py-1 rounded-md text-sm font-arabic">
                          {dw.word} ({dw.scheme_id || dw.pattern || 'غير معروف'}) × {dw.frequency}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-400 text-sm">لا توجد كلمات محفوظة لهذا الجذر.</span>
                    )}
                  </div>
                </div>
              )}
           </div>

           <div className="bg-white p-8 rounded-2xl shadow-md border border-slate-200">
              <div className="text-center mb-8">
                <SearchCheck className="w-12 h-12 text-blue-500 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-slate-800">التحقق من الصيغ</h3>
                <p className="text-slate-400 text-sm mt-1">التحليل الخوارزمي عبر خادم Python مع كشف نوع الفعل</p>
              </div>
              <div className="space-y-6">
                <div className="flex gap-4">
                  <div className="w-32">
                    <label className="block text-xs font-bold text-slate-500 mb-2 text-right">الجذر</label>
                    <input className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-4 text-center font-arabic text-2xl outline-none" value={valRoot} onChange={e => setValRoot(e.target.value)} maxLength={3} placeholder="كتب" />
                  </div>
                  <div className="flex-1">
                    <label className="block text-xs font-bold text-slate-500 mb-2 text-right">الكلمة المراد التحقق منها</label>
                    <input className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-4 text-right font-arabic text-2xl outline-none" value={valWord} onChange={e => setValWord(e.target.value)} placeholder="مثال: مكتوب" />
                  </div>
                </div>
                <button onClick={handleValidate} disabled={loading} className="w-full py-4 bg-slate-800 text-white rounded-xl font-bold hover:bg-slate-900 transition-all flex items-center justify-center gap-2">
                   {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'تحليل البنية الصرفية'}
                </button>
              </div>
           </div>

           {valResult && (
             <div className={`p-6 rounded-2xl border flex items-start gap-4 animate-in slide-in-from-top-4 ${valResult.isValid ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-red-50 border-red-200 text-red-800'}`}>
                {valResult.isValid ? <SearchCheck className="w-8 h-8 flex-shrink-0" /> : <AlertCircle className="w-8 h-8 flex-shrink-0" />}
                <div className="flex-1">
                   <h4 className="font-bold text-right">{valResult.isValid ? 'تحقق ناجح' : 'التحقق فشل'}</h4>
                   <p className="text-sm opacity-80 text-right mt-1">
                     {valResult.isValid 
                       ? `الكلمة معروفة كنمط "${valResult.scheme}".` 
                       : 'لم يتم العثور على وزن مطابق بعد التطبيع.'}
                   </p>
                   {valResult.verb_type && (
                     <p className="text-sm mt-2 text-right">نوع الفعل: <strong>{valResult.verb_type}</strong></p>
                   )}
                </div>
             </div>
           )}

           {verbTypes.length > 0 && (
             <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
               <h4 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                 <BookOpen className="w-5 h-5 text-blue-600" /> أنواع الأفعال المدعومة
               </h4>
               <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                 {verbTypes.map(verb => (
                   <div key={verb.type} className="bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-xl border border-blue-200">
                     <h5 className="font-bold text-slate-800 text-right mb-2">{verb.type}</h5>
                     <p className="text-sm text-slate-600 text-right">المثال: {verb.exemple}</p>
                     <p className="text-xs text-slate-500 text-right mt-1">{verb.caracteristiques}</p>
                   </div>
                 ))}
               </div>
             </div>
           )}
        </div>
      )}

    </Layout>
  );
};

export default App;