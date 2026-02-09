
import React from 'react';

interface TreeNode {
  name: string;
  balance: number;
  height: number;
  children?: TreeNode[];
}

const TreeNodeComp: React.FC<{ node: TreeNode }> = ({ node }) => {
  return (
    <div className="flex flex-col items-center">
      <div className="relative group">
        <div className={`
          w-14 h-14 rounded-full flex items-center justify-center border-2 transition-all duration-300 shadow-sm
          ${Math.abs(node.balance) > 1 ? 'border-red-500 bg-red-50 text-red-700' : 'border-blue-500 bg-white text-blue-700'}
          group-hover:scale-110 group-hover:shadow-lg
        `}>
          <span className="font-arabic text-xl font-bold">{node.name}</span>
          
          <div className="absolute -top-2 -right-2 bg-slate-800 text-[10px] text-white px-1.5 py-0.5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity">
            B:{node.balance}
          </div>
        </div>
      </div>

      {node.children && node.children.length > 0 && (
        <div className="flex pt-8 relative">
          {/* Connector lines */}
          <div className="absolute top-0 left-1/2 w-px h-8 bg-slate-300 -translate-x-1/2"></div>
          
          <div className="flex gap-8">
            {node.children.map((child, idx) => (
              <div key={idx} className="relative">
                <TreeNodeComp node={child} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export const TreeView: React.FC<{ data: any }> = ({ data }) => {
  if (!data) return (
    <div className="flex flex-col items-center justify-center py-12 text-slate-400 italic">
      <p>L'arbre est vide. Ajoutez une racine pour commencer.</p>
    </div>
  );

  return (
    <div className="w-full overflow-x-auto py-12 flex justify-center bg-slate-50/50 rounded-2xl border border-slate-100">
      <TreeNodeComp node={data} />
    </div>
  );
};
