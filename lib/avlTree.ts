
import { RootNodeData } from '../types';

class AVLNode {
  data: RootNodeData;
  left: AVLNode | null = null;
  right: AVLNode | null = null;
  height: number = 1;

  constructor(data: RootNodeData) {
    this.data = data;
  }
}

export class AVLTree {
  root: AVLNode | null = null;

  private getHeight(node: AVLNode | null): number {
    return node ? node.height : 0;
  }

  private getBalance(node: AVLNode | null): number {
    return node ? this.getHeight(node.left) - this.getHeight(node.right) : 0;
  }

  private rotateRight(y: AVLNode): AVLNode {
    const x = y.left!;
    const T2 = x.right;
    x.right = y;
    y.left = T2;
    y.height = Math.max(this.getHeight(y.left), this.getHeight(y.right)) + 1;
    x.height = Math.max(this.getHeight(x.left), this.getHeight(x.right)) + 1;
    return x;
  }

  private rotateLeft(x: AVLNode): AVLNode {
    const y = x.right!;
    const T2 = y.left;
    y.left = x;
    x.right = T2;
    x.height = Math.max(this.getHeight(x.left), this.getHeight(x.right)) + 1;
    y.height = Math.max(this.getHeight(y.left), this.getHeight(y.right)) + 1;
    return y;
  }

  insert(rootStr: string): void {
    if (!rootStr) return;
    const data: RootNodeData = { root: rootStr, derivedWords: [] };
    this.root = this.insertNode(this.root, data);
  }

  private insertNode(node: AVLNode | null, data: RootNodeData): AVLNode {
    if (!node) return new AVLNode(data);
    if (data.root < node.data.root) {
      node.left = this.insertNode(node.left, data);
    } else if (data.root > node.data.root) {
      node.right = this.insertNode(node.right, data);
    } else {
      return node;
    }
    node.height = 1 + Math.max(this.getHeight(node.left), this.getHeight(node.right));
    const balance = this.getBalance(node);
    if (balance > 1 && data.root < (node.left?.data.root || '')) return this.rotateRight(node);
    if (balance < -1 && data.root > (node.right?.data.root || '')) return this.rotateLeft(node);
    if (balance > 1 && data.root > (node.left?.data.root || '')) {
      node.left = this.rotateLeft(node.left!);
      return this.rotateRight(node);
    }
    if (balance < -1 && data.root < (node.right?.data.root || '')) {
      node.right = this.rotateRight(node.right!);
      return this.rotateLeft(node);
    }
    return node;
  }

  delete(rootStr: string): void {
    this.root = this.deleteNode(this.root, rootStr);
  }

  private deleteNode(node: AVLNode | null, rootStr: string): AVLNode | null {
    if (!node) return null;
    if (rootStr < node.data.root) {
      node.left = this.deleteNode(node.left, rootStr);
    } else if (rootStr > node.data.root) {
      node.right = this.deleteNode(node.right, rootStr);
    } else {
      if (!node.left || !node.right) {
        node = node.left || node.right;
      } else {
        const temp = this.getMinValueNode(node.right);
        node.data = temp.data;
        node.right = this.deleteNode(node.right, temp.data.root);
      }
    }
    if (!node) return null;
    node.height = 1 + Math.max(this.getHeight(node.left), this.getHeight(node.right));
    const balance = this.getBalance(node);
    if (balance > 1 && this.getBalance(node.left) >= 0) return this.rotateRight(node);
    if (balance > 1 && this.getBalance(node.left) < 0) {
      node.left = this.rotateLeft(node.left!);
      return this.rotateRight(node);
    }
    if (balance < -1 && this.getBalance(node.right) <= 0) return this.rotateLeft(node);
    if (balance < -1 && this.getBalance(node.right) > 0) {
      node.right = this.rotateRight(node.right!);
      return this.rotateLeft(node);
    }
    return node;
  }

  private getMinValueNode(node: AVLNode): AVLNode {
    let current = node;
    while (current.left) current = current.left;
    return current;
  }

  search(rootStr: string): RootNodeData | null {
    let current = this.root;
    while (current) {
      if (rootStr === current.data.root) return current.data;
      current = rootStr < current.data.root ? current.left : current.right;
    }
    return null;
  }

  getAllRoots(): RootNodeData[] {
    const result: RootNodeData[] = [];
    this.inOrderTraversal(this.root, result);
    return result;
  }

  private inOrderTraversal(node: AVLNode | null, result: RootNodeData[]) {
    if (node) {
      this.inOrderTraversal(node.left, result);
      result.push(node.data);
      this.inOrderTraversal(node.right, result);
    }
  }

  serialize(): string {
    return JSON.stringify(this.root);
  }

  deserialize(json: string): void {
    try {
      this.root = JSON.parse(json);
    } catch (e) {
      this.root = null;
    }
  }

  getNodesForVisual(): any {
    if (!this.root) return null;
    const mapNode = (node: AVLNode): any => ({
      name: node.data.root,
      balance: this.getBalance(node),
      height: node.height,
      children: [
        node.left ? mapNode(node.left) : null,
        node.right ? mapNode(node.right) : null
      ].filter(n => n !== null)
    });
    return mapNode(this.root);
  }
}
