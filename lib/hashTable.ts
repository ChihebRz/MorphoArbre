
import { MorphologicalScheme } from '../types';

export class HashTable {
  private size: number;
  private buckets: MorphologicalScheme[][];

  constructor(size: number = 101) {
    this.size = size;
    this.buckets = new Array(size).fill(null).map(() => []);
  }

  private hash(key: string): number {
    let total = 0;
    for (let i = 0; i < key.length; i++) {
      total = (total + key.charCodeAt(i) * (i + 1)) % this.size;
    }
    return total;
  }

  put(scheme: MorphologicalScheme): void {
    const index = this.hash(scheme.id);
    const existingIndex = this.buckets[index].findIndex(s => s.id === scheme.id);
    if (existingIndex !== -1) {
      this.buckets[index][existingIndex] = scheme;
    } else {
      this.buckets[index].push(scheme);
    }
  }

  get(id: string): MorphologicalScheme | null {
    const index = this.hash(id);
    return this.buckets[index].find(s => s.id === id) || null;
  }

  remove(id: string): void {
    const index = this.hash(id);
    this.buckets[index] = this.buckets[index].filter(s => s.id !== id);
  }

  getAll(): MorphologicalScheme[] {
    return this.buckets.flat();
  }

  serialize(): string {
    return JSON.stringify(this.buckets);
  }

  deserialize(json: string): void {
    try {
      const data = JSON.parse(json);
      if (Array.isArray(data)) this.buckets = data;
    } catch (e) {
      console.error("Failed to deserialize hash table", e);
    }
  }

  getStats(): { index: number; count: number }[] {
    return this.buckets
      .map((b, i) => ({ index: i, count: b.length }))
      .filter(stat => stat.count > 0);
  }
}
