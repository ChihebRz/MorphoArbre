 
import re
import json
import os
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False

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

def display_arabic(text: str) -> str:
    """Format Arabic text for bidirectional display (for console logs)."""
    if not ARABIC_SUPPORT or not text:
        return text
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except:
        return text

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

def detect_verb_type(root: str) -> str:
    """Detect the verb type (category) based on root composition."""
    if len(root) != 3:
        return "غير معروف"
    
    r1, r2, r3 = root[0], root[1], root[2]
    
    # Normalize: ى → ي, ا → ا (alef maqsura becomes ya)
    r3_normalized = 'ي' if r3 in ('ى', 'ي') else r3
    
    weak_letters = {'ا', 'و', 'ي'}
    hamza = 'ء'
    
    # Check hamza (at any position)
    has_hamza_start = r1 == hamza or r1 in ('أ', 'إ', 'آ')
    has_hamza_mid = r2 == hamza or r2 in ('أ', 'إ', 'آ')
    has_hamza_end = r3 == hamza or r3 in ('أ', 'إ', 'آ')
    
    # Check weak letters (original positions)
    weak_start = r1 in weak_letters
    weak_mid = r2 in weak_letters
    weak_end = r3 in weak_letters or r3 == 'ى'  # Include alef maqsura
    
    # Check for doubled letters (مضاعف)
    if r2 == r3 and r2 not in weak_letters:
        return "مضاعف"
    
    # --- Hamza Verbs (مهموز) ---
    if has_hamza_start and not has_hamza_mid and not has_hamza_end:
        return "مهموز الفاء"
    if has_hamza_mid and not has_hamza_start and not has_hamza_end:
        return "مهموز العين"
    if has_hamza_end and not has_hamza_start and not has_hamza_mid:
        return "مهموز اللام"
    
    # --- Double Weak (لفيف) ---
    # Must check BEFORE single weak patterns
    if weak_start and weak_end and not weak_mid:
        return "لفيف مفروق"  # weak at start AND end (not middle)
    if weak_start and weak_mid and not weak_end:
        return "لفيف مقرون"  # weak at start AND middle
    if weak_mid and weak_end and not weak_start:
        return "لفيف مقرون"  # weak at middle AND end
    if weak_start and weak_mid and weak_end:
        # All three weak - still لفيف
        return "لفيف مقرون"
    
    # --- Single Weak Letters ---
    # Weak at START only
    if weak_start and not weak_mid and not weak_end:
        if r1 == 'و':
            return "مثال واوي"
        elif r1 == 'ي':
            return "مثال يائي"
        else:  # ا
            return "مثال"
    
    # Weak at MIDDLE only
    if weak_mid and not weak_start and not weak_end:
        if r2 == 'و':
            return "أجوف واوي"
        elif r2 == 'ي':
            return "أجوف يائي"
        elif r2 == 'ا':
            return "أجوف"
    
    # Weak at END only (including ى)
    if weak_end and not weak_start and not weak_mid:
        if r3== 'ي' or r3 == 'ى':
            return "ناقص يائي"
        elif r3 == 'و':
            return "ناقص واوي"
        elif r3 == 'ا':
            return "ناقص ألفي"
    
    # --- Regular (صحيح سالم) ---
    # No hamza, no weak letters
    if not has_hamza_start and not has_hamza_mid and not has_hamza_end:
        if not weak_start and not weak_mid and not weak_end:
            return "صحيح سالم"
    
    return "غير معروف"

def identify_pattern_type(pattern: str) -> str:
    """Identify which morphological form a pattern represents.
    Returns: 'past', 'present', 'imperative', 'agent', 'patient', 'unknown'
    """
    pattern_norm = normalize_arabic(pattern)
    
    # Agent noun (اسم الفاعل)
    if 'فاعل' in pattern_norm:
        return 'agent'
    
    # Patient noun (اسم المفعول)
    if 'مفعول' in pattern_norm:
        return 'patient'
    
    # Imperative (الأمر)
    if pattern_norm.startswith('اف'):
        return 'imperative'
    
    # Present (المضارع) - starts with ي، ت، ن، أ
    if pattern and pattern[0] in 'يتنأ':
        return 'present'
    
    # Past (الماضي) - default for فعل-type patterns
    if 'فعل' in pattern_norm and pattern_norm[0] == 'ف':
        return 'past'
    
    return 'unknown'

def apply_verb_transformations(word: str, root: str, verb_type: str, pattern: str) -> str:
    """Apply morphological transformations based on verb type and pattern.
    
    Follows the complete Arabic morphological rules for:
    1. صحيح سالم (Regular)
    2. مهموز (Hamza verbs)
    3. مثال (Weak at start)
    4. أجوف (Weak at middle)
    5. ناقص (Weak at end)
    6. مضاعف (Doubled)
    7. لفيف (Double weak)
    """
    
    # Normalize both word and pattern
    word_norm = normalize_arabic(word)
    pattern_type = identify_pattern_type(pattern)
    
    # === 1. صحيح سالم (Regular verbs) ===
    # No transformations needed - return directly
    if verb_type == "صحيح سالم":
        return word_norm
    
    # === 2. مضاعف (Doubled letters) ===
    # عين = لام, stays as is
    if verb_type == "مضاعف":
        return word_norm
    
    # === 3. مهموز الفاء (Hamza at ROOT START) ===
    if verb_type == "مهموز الفاء":
        if pattern_type == 'agent':
            # ف = ء, ع, ل → اء + ع + ل → آ + ع + ل
            if word_norm.startswith('اا'):
                return 'آ' + word_norm[2:]
            return word_norm
        elif pattern_type == 'imperative':
            # اف + ع + ل → (drop ا marking hamza) → ف + ع + ل
            if len(word_norm) > 1 and word_norm[0] == 'ا':
                return word_norm[1:]
            return word_norm
        else:
            # past, present, patient: return as-is
            return word_norm
    
    # === 4. مهموز العين (Hamza at ROOT MIDDLE) ===
    if verb_type == "مهموز العين":
        # ع = ء, follow أجوف pattern for agent
        if pattern_type == 'agent':
            # Pattern: فاعل → ف + اء + ل → ف + ا + ل
            # But when doubled: فاال → فائ ل
            if 'اا' in word_norm:
                return word_norm.replace('اا', 'ائ', 1)
            return word_norm
        else:
            return word_norm
    
    # === 5. مهموز اللام (Hamza at ROOT END) ===
    if verb_type == "مهموز اللام":
        # ل = ء, mostly behaves like ناقص
        if pattern_type == 'agent':
            # فعل with ل=ء → فاعل but ends in ء
            return word_norm
        else:
            return word_norm
    
    # === 6. مثال واوي/يائي (WEAK AT START) ===
    if verb_type in ["مثال واوي", "مثال يائي", "مثال"]:
        r1 = root[0]
        weak_char = r1  # و or ي
        
        if pattern_type == 'imperative':
            # Imperative drops the weak start: وجد + أمر → جد (not وجد)
            if len(word_norm) > 0 and word_norm[0] in ['و', 'ي']:
                return word_norm[1:]
            return word_norm
        elif pattern_type == 'present':
            # Present: الواو تسقط في المضارع
            # وجد → يجد (not يوجد)
            if len(word_norm) > 0 and word_norm[0] in ['و', 'ي']:
                return word_norm[1:]
            return word_norm
        else:
            # past, agent, patient: can keep weak letter
            return word_norm
    
    # === 7. أجوف واوي/يائي (WEAK AT MIDDLE) ===
    if verb_type in ["أجوف", "أجوف واوي", "أجوف يائي"]:
        if pattern_type == 'agent':
            # ف + ا + ع + ل (pattern) with ع=و/ي
            # Pattern: فاعل → قاال → قائل
            if 'اا' in word_norm:
                return word_norm.replace('اا', 'ائ', 1)
            return word_norm
        
        elif pattern_type == 'patient':
            # Pattern: مفعول = م + ف + و + ع + ل
            # For أجوف: م + ف + و + ا + ل (weak ع inserted as ا)
            # Result should be مفول (not مفاول)
            if 'اول' in word_norm:
                # Remove the inserted weak alef before و
                return word_norm.replace('اول', 'ول', 1)
            return word_norm
        
        elif pattern_type == 'imperative':
            # Pattern: اف + ع + ل
            # For أجوف: اف + ا + ل (weak ع inserted as ا)
            # Result should be اف + ل (keep consonants) = اقل (not اقال)
            if 'ال' in word_norm and word_norm.startswith('ا'):
                # Keep first (ا from imperative) and last consonant
                return word_norm[0] + word_norm[-1]
            return word_norm
        
        elif pattern_type == 'present':
            # Present: ي + ف + و/ل + ع + ل
            # For أجوف: يفول/يفيل
            return word_norm
        
        else:  # past
            return word_norm
    
    # === 8. ناقص يائي (WEAK ي AT END) ===
    if verb_type == "ناقص يائي":
        if pattern_type == 'agent':
            # بقي + فاعل → بقي → باقي BUT rule says drop ي → باق
            # رمى + فاعل → رما (after norm) → رام
            return word_norm.rstrip('ي')
        
        elif pattern_type == 'patient':
            # Pattern مفعول: م + ف + ع + و + ل
            # ناقص ي: م + ب + ق + و + ي → مبقوي
            # Keep as-is (و from pattern + ي from root end)
            return word_norm
        
        elif pattern_type == 'imperative':
            # اف + ع + ل with ل=ي
            # Result: ابق (drop final ي)
            return word_norm.rstrip('ي')
        
        elif pattern_type == 'present':
            # Present: ي + ف + ع + و/ي
            # يبقى (with ى instead of ي)
            if word_norm.endswith('ي'):
                return word_norm[:-1] + 'ى'
            return word_norm
        
        else:
            return word_norm
    
    # === 9. ناقص واوي/ألفي (WEAK ا/و AT END) ===
    if verb_type in ["ناقص واوي", "ناقص ألفي"]:
        if pattern_type == 'agent':
            # دعا + فاعل → داعا BUT rule says drop final ا → داع
            return word_norm.rstrip('او')
        
        elif pattern_type == 'patient':
            # Pattern مفعول: م + د + ع + و + ا
            # Rule: final ا→و so مدعو
            if word_norm.endswith('ا'):
                return word_norm[:-1] + 'و'
            return word_norm
        
        elif pattern_type == 'imperative':
            # ادعا + أمر → drop ا at end → ادع
            return word_norm.rstrip('او')
        
        elif pattern_type == 'present':
            # يدعا → يدعو (final ا→و in present)
            if word_norm.endswith('ا'):
                return word_norm[:-1] + 'و'
            return word_norm
        
        else:
            return word_norm
    
    # === 10. لفيف مفروق (WEAK AT START + END) ===
    if verb_type == "لفيف مفروق":
        if pattern_type == 'agent':
            # وقى + فاعل → واقي BUT rule says drop final → واق
            return word_norm.rstrip('ي')
        else:
            return word_norm
    
    # === 11. لفيف مقرون (WEAK AT MIDDLE + END) ===
    if verb_type == "لفيف مقرون":
        if pattern_type == 'agent':
            # طوى + فاعل → طاوي BUT rule says drop final → طاو
            return word_norm.rstrip('ي')
        elif pattern_type == 'present':
            # يطوي / يطيي
            return word_norm
        else:
            return word_norm
    
    # === DEFAULT ===
    return word_norm


# --- Data Structures ---

class DerivedWord(BaseModel):
    word: str
    frequency: int = 1

class RootNodeData(BaseModel):
    root: str
    derived_words: List[DerivedWord] = []
    verb_type: Optional[str] = None  # Added: verb type detection


class VerbTypeInfo(BaseModel):
    type: str
    exemple: str
    probleme: str
    caracteristiques: str
    transformations: Dict

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
            return AVLNode(RootNodeData(root=root_str, verb_type=detect_verb_type(root_str)))
        if root_str < node.data.root:
            node.left = self._insert(node.left, root_str)
        elif root_str > node.data.root:
            node.right = self._insert(node.right, root_str)
        else:
            # Update verb type in case it was recalculated
            node.data.verb_type = detect_verb_type(root_str)
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

# --- App State & Persistence ---

root_tree = AVLTree()
scheme_table = HashTable()

# Updated paths to use data/ folder
ROOTS_DATA_FILE = "data/roots_data.json"
SCHEMES_DATA_FILE = "data/schemes_data.json"
VERB_RULES_FILE = "data/rules_verbs.json"

# Load verb rules on startup
VERB_RULES = []
def load_verb_rules():
    """Load verb type rules from JSON file."""
    global VERB_RULES
    if not os.path.exists(VERB_RULES_FILE):
        VERB_RULES = []
        return
    try:
        with open(VERB_RULES_FILE, "r", encoding="utf-8") as f:
            VERB_RULES = json.load(f)
    except Exception as e:
        print(f"Error loading verb rules: {e}")
        VERB_RULES = []

def get_verb_info(verb_type: str) -> Optional[VerbTypeInfo]:
    """Get detailed information about a verb type."""
    for rule in VERB_RULES:
        if rule.get("type") == verb_type:
            return VerbTypeInfo(**rule)
    return None


def save_roots_to_disk():
    """Persist all roots (with historique) to a JSON file."""
    data = []
    for r in root_tree.get_all():
        # r is RootNodeData
        data.append({
            "root": r.root,
            "verb_type": r.verb_type,
            "derived_words": [
                {"word": dw.word, "frequency": dw.frequency}
                for dw in r.derived_words
            ]
        })
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    with open(ROOTS_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_roots_from_disk():
    """Load roots (and historique) from disk if the file exists."""
    if not os.path.exists(ROOTS_DATA_FILE):
        return False
    try:
        with open(ROOTS_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return False

    for item in data:
        root_str = item.get("root")
        if not root_str:
            continue
        root_tree.insert(root_str)
        node_data = root_tree.search(root_str)
        if not node_data:
            continue
        # Always recalculate verb_type to ensure it's current
        node_data.verb_type = detect_verb_type(root_str)
        node_data.derived_words = [
            DerivedWord(word=dw.get("word", ""), frequency=dw.get("frequency", 1))
            for dw in item.get("derived_words", [])
        ]
    return True


def init_roots_in_memory():
    """Initialize default roots with all verb types when no saved data exists."""
    roots = [
        # صحيح سالم (Regular)
        "كتب", "رسم", "درس", "خرج",
        # مهموز الفاء
        "أكل",
        # مهموز العين
        "سأل",
        # مهموز اللام
        "ملأ",
        # مثال واوي
        "وجد",
        # أجوف واوي
        "قال",
        # أجوف يائي
        "باع",
        # ناقص يائي
        "بقي", "رمى",
        # ناقص واوي
        "دعا",
        # لفيف مفروق
        "وقى",
        # لفيف مقرون
        "طوى",
        # مضاعف
        "مدد",
    ]
    for r in roots:
        root_tree.insert(r)


def save_schemes_to_disk():
    """Persist all schemes (hash table) to a JSON file."""
    data = []
    for s in scheme_table.get_all():
        data.append({
            "id": s.id,
            "pattern": s.pattern,
            "transformationRule": s.transformationRule,
        })
    os.makedirs("data", exist_ok=True)
    with open(SCHEMES_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_schemes_from_disk() -> bool:
    """Load schemes from disk if the file exists."""
    if not os.path.exists(SCHEMES_DATA_FILE):
        return False
    try:
        with open(SCHEMES_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return False

    for item in data:
        sid = item.get("id")
        pattern = item.get("pattern")
        rule = item.get("transformationRule", "")
        if not sid or not pattern:
            continue
        scheme_table.put(MorphologicalScheme(id=sid, pattern=pattern, transformationRule=rule))
    return True


def init_schemes_in_memory():
    """Initialize 5 essential morphological schemes in the hash table."""
    schemes = [
        ("فعل", "فَعَلَ", "المصدر (Infinitive)"),
        ("يفعل", "يَفْعَلُ", "صيغة المضارع (Present)"),
        ("أمر", "افْعَل", "صيغة الأمر (Imperative)"),
        ("فاعل", "فَاعِل", "اسم الفاعل (Agent Noun)"),
        ("مفعول", "مَفْعُول", "اسم المفعول (Patient Noun)"),
    ]
    for scheme_id, pattern, rule in schemes:
        scheme_table.put(MorphologicalScheme(id=scheme_id, pattern=pattern, transformationRule=rule))


# On startup: try to load roots from disk, otherwise use defaults and save them
if not load_roots_from_disk():
    init_roots_in_memory()
    save_roots_to_disk()

# On startup: try to load schemes from disk, otherwise use defaults and save them
if not load_schemes_from_disk():
    init_schemes_in_memory()
    save_schemes_to_disk()

# Load verb rules on startup
load_verb_rules()

# --- API Endpoints ---

@app.get("/api/roots")
def get_roots():
    return root_tree.get_all()

@app.get("/api/roots/visual")
def get_roots_visual():
    return root_tree.get_visual()

@app.get("/api/roots/{root}")
def get_root_details(root: str):
    """Get detailed information about a specific root."""
    root_data = root_tree.search(root)
    if not root_data:
        raise HTTPException(404, "Root not found")
    return {
        "root": root_data.root,
        "verb_type": root_data.verb_type,
        "verb_info": get_verb_info(root_data.verb_type) if root_data.verb_type else None,
        "derived_words": root_data.derived_words
    }

@app.get("/api/verb-types")
def get_verb_types():
    """Get all verb types and their rules."""
    return VERB_RULES

@app.get("/api/verb-types/{verb_type}")
def get_verb_type_details(verb_type: str):
    """Get detailed information about a specific verb type."""
    for rule in VERB_RULES:
        if rule.get("type") == verb_type:
            return rule
    raise HTTPException(404, "Verb type not found")

@app.post("/api/roots")
def add_root(root: str):
    if len(root) != 3: raise HTTPException(400, "Root must be 3 chars")
    root_tree.insert(root)
    save_roots_to_disk()
    root_data = root_tree.search(root)
    return {
        "status": "ok",
        "root": root,
        "verb_type": root_data.verb_type if root_data else None
    }

@app.get("/api/schemes")
def get_schemes():
    return scheme_table.get_all()

@app.post("/api/schemes")
def add_scheme(scheme: MorphologicalScheme):
    scheme_table.put(scheme)
    save_schemes_to_disk()
    return {"status": "ok"}

@app.post("/api/generate")
def generate(root: str, scheme_id: str):
    """Generate a word by applying a scheme to a root."""
    scheme = scheme_table.get(scheme_id)
    if not scheme: raise HTTPException(404, "Scheme not found")
    
    # Get root data to include verb type
    root_data = root_tree.search(root)
    if not root_data:
        raise HTTPException(404, "Root not found")
    
    word = apply_pattern(root, scheme.pattern)
    verb_type = root_data.verb_type
    
    # Apply verb-specific transformations (pass pattern for context)
    word = apply_verb_transformations(word, root, verb_type, scheme.pattern)
    
    # Record in history
    existing = next((d for d in root_data.derived_words if d.word == word), None)
    if existing:
        existing.frequency += 1
    else:
        root_data.derived_words.append(DerivedWord(word=word))
    save_roots_to_disk()
    
    return {
        "word": word,
        "root": root,
        "scheme": scheme_id,
        "verb_type": verb_type
    }

@app.post("/api/validate")
def validate(word: str, root_str: str):
    """Validate if a word can be derived from a root using any scheme."""
    norm_input = normalize_arabic(word)
    
    # Check if root exists
    root_data = root_tree.search(root_str)
    if not root_data:
        raise HTTPException(404, "Root not found")
    
    schemes = scheme_table.get_all()
    
    found_scheme = None
    for s in schemes:
        generated = apply_pattern(root_str, s.pattern)
        if normalize_arabic(generated) == norm_input:
            found_scheme = s.id
            break
            
    if found_scheme:
        # Record in history
        existing = next((d for d in root_data.derived_words if d.word == word), None)
        if existing:
            existing.frequency += 1
        else:
            root_data.derived_words.append(DerivedWord(word=word))
        save_roots_to_disk()
        return {
            "isValid": True,
            "scheme": found_scheme,
            "verb_type": root_data.verb_type
        }
    
    return {
        "isValid": False,
        "verb_type": root_data.verb_type
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
