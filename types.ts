
export interface DerivedWord {
  word: string;
  frequency: number;
  timestamp: number;
}

export interface RootNodeData {
  root: string; // The triliteral root, e.g., "كتب"
  derivedWords: DerivedWord[];
}

export interface MorphologicalScheme {
  id: string; // Unique identifier (the name, e.g., "مفعول")
  pattern: string; // The abstract representation, e.g., "مفْعول"
  transformationRule: string; // A description or code for the rule
}

export enum TabType {
  DASHBOARD = 'DASHBOARD',
  ROOTS = 'ROOTS',
  SCHEMES = 'SCHEMES',
  GENERATOR = 'GENERATOR',
  VALIDATOR = 'VALIDATOR'
}
