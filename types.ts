
export interface DerivedWord {
  word: string;
  frequency: number;
  timestamp?: number;
  scheme_id?: string;
  pattern?: string;
}

export interface RootNodeData {
  root: string;
  derivedWords: DerivedWord[];
  verb_type?: string;
}

export interface MorphologicalScheme {
  id: string;
  pattern: string;
  transformationRule: string;
}

export interface VerbTypeTransformation {
  regles: string[];
  exemples?: string[];
}

export interface VerbTypeInfo {
  type: string;
  exemple: string;
  probleme: string;
  caracteristiques: string;
  transformations: VerbTypeTransformation;
}

export enum TabType {
  DASHBOARD = 'DASHBOARD',
  ROOTS = 'ROOTS',
  SCHEMES = 'SCHEMES',
  GENERATOR = 'GENERATOR',
  VALIDATOR = 'VALIDATOR'
}
