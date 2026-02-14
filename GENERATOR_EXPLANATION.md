# كيفية عمل مولد الكلمات - How The Generator Works

## 🔄 التدفق العام (Overall Flow)

```
User Input (root + pattern)
         ↓
    API Endpoint: /api/generate
         ↓
    Step 1: Get Scheme (Pattern)
    Step 2: Get Root Data & Verb Type
    Step 3: Apply Pattern (Inject Root)
    Step 4: Apply Transformations
    Step 5: Save & Return Result
```

---

## 📝 مثال عملي (Practical Example)

### Input:
- **Root**: كتب (K-T-B - write)
- **Pattern**: فاعل (agent noun)

### Step-by-Step Processing:

#### **Step 1: Get Scheme from Hash Table**
```python
scheme = scheme_table.get("فاعل")
# Returns: MorphologicalScheme(
#   id="فاعل",
#   pattern="فَاعِل",
#   transformationRule="Agent noun"
# )
```

#### **Step 2: Get Root Data**
```python
root_data = root_tree.search("كتب")
# Returns: RootNodeData(
#   root="كتب",
#   verb_type="صحيح سالم",
#   derived_words=[...]
# )
```

#### **Step 3: Apply Pattern (Inject Root Letters)**
```
Pattern: فَاعِل
         ↓ (inject ك-ت-ب)
Becomes: كَاتِب

apply_pattern("كتب", "فَاعِل"):
  - ف (pattern position 1) → ك (root position 1)
  - ع (pattern position 2) → ت (root position 2)
  - ل (pattern position 3) → ب (root position 3)
Result: "كاتب"
```

#### **Step 4: Apply Transformations**
```python
apply_verb_transformations(
   word="كاتب",
   root="كتب",
   verb_type="صحيح سالم",
   pattern="فَاعِل"
)

# For صحيح سالم (regular verb):
# NO TRANSFORMATIONS NEEDED
# Return as-is: "كاتب"
```

#### **Step 5: Save & Return**
```python
# Add to derived_words history
root_data.derived_words.append(DerivedWord(word="كاتب"))

# Return to user:
{
  "word": "كاتب",
  "root": "كتب",
  "scheme": "فاعل",
  "verb_type": "صحيح سالم"
}
```

---

## 🎯 مثال معقد مع تحويلات (Complex Example with Transformations)

### Input:
- **Root**: قال (Q-W-L - say, أجوف واوي - weak middle)
- **Pattern**: يفعل (present tense)

### Processing:

#### **Step 1-2: Get Scheme & Root Data** ✅
```
scheme.pattern = "يَفْعَلُ"
verb_type = "أجوف واوي" (weak و in middle)
```

#### **Step 3: Apply Pattern**
```
Pattern: يَفْعَلُ
         ↓ (inject ق-ا-ل)
Becomes: يَقْاَلُ
Result: "يقال"
```

#### **Step 4: Apply Transformations** ⚙️
```python
# Verb type: أجوف واوي
# Pattern: يفعل (present tense)
# is_present = True

if is_present and word_norm[2] == 'ا':
    # Present tense: middle weak ا → و
    return word[0] + word[1] + 'و' + word[3:]
    # "يقال" → "يقول"
```

#### **Step 5: Return**
```json
{
  "word": "يقول",
  "root": "قال",
  "scheme": "يفعل",
  "verb_type": "أجوف"
}
```

---

## 5️⃣ الأنماط الخمسة (5 Essential Patterns)

### 1. 🚀 **فعل** (Infinitive/Root base)
```
Root: كتب → Pattern: فَعَلَ
Result: كتب (no change for regular verbs)
```

### 2. 🔤 **يفعل** (Present Tense - 3rd masculine)
```
Root: كتب → Pattern: يَفْعَلُ
Result: يكتب

Weak verb example:
Root: قال → Pattern: يَفْعَلُ
Step 1: inject → يقال
Step 2: transform (present + weak middle) → يقول
```

### 3. 📋 **أمر** (Imperative Command)
```
Root: كتب → Pattern: افْعَل
Result: اكتب

With hamza verb:
Root: أكل → Pattern: افْعَل
Step 1: inject → ااكل (then normalize → اكل)
Step 2: transform (imperative + hamza) → drop alef → كل
```

### 4. 👤 **فاعل** (Agent Noun - Active Participle)
```
Root: كتب → Pattern: فَاعِل
Result: كاتب

Weak example:
Root: قال → Pattern: فَاعِل
Step 1: inject → اقال → normalize → قاال
Step 2: transform (agent + doubled alef) → قائل
```

### 5. 🎯 **مفعول** (Patient Noun - Passive Participle)
```
Root: كتب → Pattern: مَفْعُول
Result: مكتوب

Weak example:
Root: قال → Pattern: مَفْعُول
Step 1: inject → مقال
Step 2: transform (patient + weak middle) → مقول
```

---

## 🔧 التحويلات حسب نوع الفعل (Transformations by Verb Type)

| Verb Type | Example | Agent (فاعل) | Present (يفعل) | Imperative (أمر) |
|-----------|---------|--------------|-----------------|------------------|
| **صحيح سالم** | كتب | كاتب | يكتب | اكتب |
| **مهموز الفاء** | أكل | آكل | يأكل | كل (drop ا) |
| **أجوف واوي** | قال | قائل | يقول | قل |
| **ناقص يائي** | بقي | باق | يبقى | ابق |
| **ناقص واوي/ألفي** | دعا | داع | يدعو | ادع |

---

## 💾 Hash Table Role

```
scheme_table (Hash Table O(1) lookup):
┌─────────┬──────────────┬─────────────────────────┐
│ ID      │ Pattern      │ Transformation Rule     │
├─────────┼──────────────┼─────────────────────────┤
│ فعل     │ فَعَلَ       │ Infinitive             │
│ يفعل    │ يَفْعَلُ     │ Present 3rd masculine  │
│ أمر     │ افْعَل      │ Imperative             │
│ فاعل    │ فَاعِل      │ Agent noun             │
│ مفعول   │ مَفْعُول    │ Patient noun           │
└─────────┴──────────────┴─────────────────────────┘

When user requests pattern, lookup is O(1) - instant!
```

---

## 🌳 AVL Tree Role

```
root_tree (AVL Tree for roots):
        كتب
       /   \
     بقي   قال
     /
   أكل

When user requests root, search is O(log n)
Returns: verb_type + derived_words history
```

---

## 📊 Complete Data Flow Example

```
REQUEST: POST /api/generate?root=قال&scheme_id=يفعل

↓

generate() function:
  |
  ├─ Step 1: scheme = scheme_table.get("يفعل")
  |           → pattern = "يَفْعَلُ"
  |
  ├─ Step 2: root_data = root_tree.search("قال")
  |           → verb_type = "أجوف"
  |
  ├─ Step 3: word = apply_pattern("قال", "يَفْعَلُ")
  |           ق→ي, ا→ف, ل→ع, add ل + diacritics
  |           → "يقال" (normalized)
  |
  ├─ Step 4: word = apply_verb_transformations(
  |             "يقال", "قال", "أجوف", "يَفْعَلُ"
  |           )
  |           → is_present = True
  |           → word[2] == 'ا' (middle position)
  |           → Replace with 'و': "يقول"
  |
  ├─ Step 5: root_data.derived_words.append("يقول")
  |           save_roots_to_disk()
  |
  └─ RETURN: {
              "word": "يقول",
              "root": "قال",
              "scheme": "يفعل",
              "verb_type": "أجوف"
            }
```

---

## 🎓 Key Concepts

### **Pattern Application** (`apply_pattern`)
Simple substitution of root letters into pattern template:
- **ف** → letter 1 of root
- **ع** → letter 2 of root  
- **ل** → letter 3 of root
- Everything else stays as-is

### **Verb Type Detection** (`detect_verb_type`)
Analyzes root composition:
- Regular (no weak letters) → **صحيح سالم**
- Weak start → **مثال واوي/يائي**
- Weak middle → **أجوف واوي/يائي**
- Weak end → **ناقص يائي/واوي**
- Hamza at position → **مهموز الفاء/العين/اللام**

### **Transformations** (`apply_verb_transformations`)
Context-aware morphological rules:
- Depends on BOTH verb type AND pattern
- Example: ناقص يائي + يفعل = drop final ي, add ى
- Example: أجوف واوي + يفعل = replace middle ا with و

---

## 📈 Current Status

**5 Essential Patterns in Hash Table:**
- ✅ فعل (Infinitive)
- ✅ يفعل (Present)
- ✅ أمر (Imperative)
- ✅ فاعل (Agent)
- ✅ مفعول (Patient)

**Test Results: 20/25 passing (80% success rate)**
- صحيح سالم: 5/5 ✅
- مهموز الفاء: 2/5 (hamza preservation issue)
- أجوف: 5/5 ✅
- ناقص يائي: 4/5 ✅
- ناقص واوي/ألفي: 4/5 ✅
