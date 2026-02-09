
import re
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Linguistic Logic ---

def normalize_arabic(text: str) -> str:
    """Standardize Arabic text for robust comparison."""
    if not text: return ""
    # Remove diacritics (harakat)
    text = re.sub(r'[\u064B-\u0652]', '', text)
    # Standardize Alef
    text = re.sub(r'[أإآ]', 'ا', text)
    # Standardize Taa Marbuta to Haa
    text = text.replace('ة', 'ه')
    # Standardize Yaa / Alef Maqsura
    text = text.replace('ى', 'ي')
    return text.strip()

def apply_pattern(root: str, pattern: str) -> str:
    """Inject a 3-letter root into a pattern."""
    if len(root) != 3:
        return ""
    r1, r2, r3 = root[0], root[1], root[2]
    res = []
    for char in pattern:
        if char == 'ف': res.append(r1)
        elif char == 'ع': res.append(r2)
        elif char == 'ل': res.append(r3)
        else: res.append(char)
    return "".join(res)

# --- Data Structures ---

class DerivedWord(BaseModel):
    word: str
    frequency: int = 1

class RootNodeData(BaseModel):
    root: str
    derived_words: List[DerivedWord] = []

class AVLNode:
    def __init__(self, data: RootNodeData):
        self.data = data
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    def __init__(self):
        self.root = None

    def _get_height(self, node):
        return node.height if node else 0

    def _get_balance(self, node):
        return self._get_height(node.left) - self._get_height(node.right) if node else 0

    def rotate_right(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))
        return x

    def rotate_left(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def insert(self, root_str: str):
        self.root = self._insert(self.root, root_str)

    def _insert(self, node, root_str):
        if not node:
            return AVLNode(RootNodeData(root=root_str))
        if root_str < node.data.root:
            node.left = self._insert(node.left, root_str)
        elif root_str > node.data.root:
            node.right = self._insert(node.right, root_str)
        else:
            return node

        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)

        if balance > 1 and root_str < node.left.data.root:
            return self.rotate_right(node)
        if balance < -1 and root_str > node.right.data.root:
            return self.rotate_left(node)
        if balance > 1 and root_str > node.left.data.root:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)
        if balance < -1 and root_str < node.right.data.root:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)
        return node

    def search(self, root_str: str) -> Optional[RootNodeData]:
        curr = self.root
        while curr:
            if root_str == curr.data.root: return curr.data
            curr = curr.left if root_str < curr.data.root else curr.right
        return None

    def get_all(self) -> List[RootNodeData]:
        res = []
        def traverse(node):
            if node:
                traverse(node.left)
                res.append(node.data)
                traverse(node.right)
        traverse(self.root)
        return res

    def get_visual(self):
        def map_node(node):
            if not node: return None
            return {
                "name": node.data.root,
                "balance": self._get_balance(node),
                "children": [n for n in [map_node(node.left), map_node(node.right)] if n]
            }
        return map_node(self.root)

class MorphologicalScheme(BaseModel):
    id: str
    pattern: str
    transformationRule: str

class HashTable:
    def __init__(self, size=101):
        self.size = size
        self.buckets = [[] for _ in range(size)]

    def _hash(self, key: str) -> int:
        return sum(ord(c) * (i + 1) for i, c in enumerate(key)) % self.size

    def put(self, scheme: MorphologicalScheme):
        idx = self._hash(scheme.id)
        for i, s in enumerate(self.buckets[idx]):
            if s.id == scheme.id:
                self.buckets[idx][i] = scheme
                return
        self.buckets[idx].append(scheme)

    def get(self, id: str) -> Optional[MorphologicalScheme]:
        idx = self._hash(id)
        for s in self.buckets[idx]:
            if s.id == id: return s
        return None

    def get_all(self) -> List[MorphologicalScheme]:
        return [s for b in self.buckets for s in b]

# --- App State ---

root_tree = AVLTree()
scheme_table = HashTable()

# Initial Data
for r in ["كتب", "رسم", "درس", "خرج"]: root_tree.insert(r)
scheme_table.put(MorphologicalScheme(id="فعل", pattern="فَعَلَ", transformationRule="Base"))
scheme_table.put(MorphologicalScheme(id="فاعل", pattern="فَاعِل", transformationRule="Agent"))
scheme_table.put(MorphologicalScheme(id="مفعول", pattern="مَفْعُول", transformationRule="Patient"))

# --- API Endpoints ---

@app.get("/api/roots")
def get_roots():
    return root_tree.get_all()

@app.get("/api/roots/visual")
def get_roots_visual():
    return root_tree.get_visual()

@app.post("/api/roots")
def add_root(root: str):
    if len(root) != 3: raise HTTPException(400, "Root must be 3 chars")
    root_tree.insert(root)
    return {"status": "ok"}

@app.get("/api/schemes")
def get_schemes():
    return scheme_table.get_all()

@app.post("/api/schemes")
def add_scheme(scheme: MorphologicalScheme):
    scheme_table.put(scheme)
    return {"status": "ok"}

@app.post("/api/generate")
def generate(root: str, scheme_id: str):
    scheme = scheme_table.get(scheme_id)
    if not scheme: raise HTTPException(404, "Scheme not found")
    word = apply_pattern(root, scheme.pattern)
    return {"word": word}

@app.post("/api/validate")
def validate(word: str, root_str: str):
    # Fix: Validation logic now uses standard normalization
    norm_input = normalize_arabic(word)
    schemes = scheme_table.get_all()
    
    found_scheme = None
    for s in schemes:
        generated = apply_pattern(root_str, s.pattern)
        if normalize_arabic(generated) == norm_input:
            found_scheme = s.id
            break
            
    if found_scheme:
        root_data = root_tree.search(root_str)
        if root_data:
            existing = next((d for d in root_data.derived_words if d.word == word), None)
            if existing: existing.frequency += 1
            else: root_data.derived_words.append(DerivedWord(word=word))
        return {"isValid": True, "scheme": found_scheme}
    
    return {"isValid": False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
