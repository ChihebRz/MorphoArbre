 
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
    # Remove short vowels / shadda / sukun but KEEP tanween (ً ٌ ٍ)
    text = re.sub(r'[\u064E-\u0652]', '', text)
    # Keep hamza (أ إ آ) - only normalize shapes, do NOT convert to ا
    text = text.replace('إ', 'أ').replace('آ', 'أ')
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

def expand_ajwaf_root_for_pattern(root: str, verb_type: str) -> str:
    """
    For أجوف roots stored as past (قال, باع), expand middle ا to و/ي.
    فاعل with قول → قاول; with بيع → بائع. Then rules ou→ائ, ai→ائ apply.
    """
    if len(root) != 3 or root[1] != 'ا':
        return root
    if "أجوف" not in verb_type:
        return root
    r1, r3 = root[0], root[2]
    if "واوي" in verb_type:
        return r1 + "و" + r3  # قال → قول
    if "يائي" in verb_type:
        return r1 + "ي" + r3  # باع → بيع
    return r1 + "و" + r3  # default أجوف


def apply_pattern(root: str, pattern: str, verb_type: Optional[str] = None) -> str:
    """Inject a 3-letter root into a pattern. For أجوف, uses expanded root (قول not قال)."""
    if len(root) != 3:
        return ""
    root = expand_ajwaf_root_for_pattern(root, verb_type or "")
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
        # Weak at start AND middle (لفيف مقرون)
        if r1 == 'و' and r2 == 'ي':
            return "لفيف مقرون واوي"
        elif r1 == 'ي' and r2 == 'ي':
            return "لفيف مقرون يائي"
        else:
            return "لفيف مقرون"
    
    if weak_mid and weak_end and not weak_start:
        # Weak at middle AND end (could be also لفيف مقرون)
        if r2 == 'و' and r3 == 'ي':
            return "لفيف مقرون واوي"
        elif r2 == 'ي' and r3 == 'ي':
            return "لفيف مقرون يائي"
        else:
            return "لفيف مقرون"
    
    if weak_start and weak_mid and weak_end:
        # All three weak - still لفيف
        if r1 == 'و' and r2 == 'ي' and r3 in ('ي', 'ى'):
            return "لفيف مقرون واوي"
        elif r1 == 'ي' and r2 == 'ي' and r3 in ('ي', 'ى'):
            return "لفيف مقرون يائي"
        else:
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

def identify_pattern_type(pattern: str, scheme_id: str = "") -> str:
    """Identify which morphological form a pattern represents by scheme_id.
    Scheme ID is more reliable than pattern string matching.
    """
    # Use scheme_id if we can determine it from context
    scheme_id_norm = scheme_id.lower().strip()
    
    if 'فاعل' in scheme_id_norm:
        return 'agent'
    if 'مفعول' in scheme_id_norm:
        return 'patient'
    if 'أمر' in scheme_id_norm:
        return 'imperative'
    if 'يفعل' in scheme_id_norm:
        return 'present'
    if 'فعل' in scheme_id_norm and 'اعل' not in scheme_id_norm:  # Avoid matching فاعل
        return 'past'
    
    # Fallback to pattern matching
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

def apply_verb_transformations(word: str, root: str, verb_type: str, pattern: str, scheme_id: str = "") -> str:
    """Apply morphological transformations based on verb type and pattern."""
    
    if not root or len(root) < 3:
        return word
    
    # Keep original root with hamza
    r1_orig, r2_orig, r3_orig = root[0], root[1], root[2]
    word_norm = normalize_arabic(word)
    pattern_type = identify_pattern_type(pattern, scheme_id)
    
    # Helper: restore hamza at specific position
    def restore_hamza(text, pos, char):
        if pos < len(text):
            # Accept any form of hamza: أ، إ، آ، ء
            if char in ('أ', 'إ', 'آ', 'ء'):
                return text[:pos] + char + text[pos+1:]
        return text

    # Helper: fix ناقص مفعول - safely remove inserted و before last root letter
    def fix_naqis_patient(w: str, r: str) -> str:
        # Only remove an internal و; never touch a final و
        if len(w) < 3:
            return w
        for i in range(len(w) - 1):
            if w[i] == 'و':
                return w[:i] + w[i+1:]
        return w

    # === 0. صحيح سالم ===
    if verb_type == "صحيح سالم":
        return word_norm
    
    # === 1. مضاعف ===
    if verb_type == "مضاعف":
        if pattern_type == 'imperative' and word_norm.startswith('ا'):
            return word_norm[1:]
        return word_norm
    
    # === 1.5. مهموز الفاء (Hamza at START) ===
    if verb_type == "مهموز الفاء":
        if pattern_type == 'past':
            return restore_hamza(word_norm, 0, r1_orig)

        elif pattern_type == 'present':
            if word_norm and word_norm[0] == 'ي':
                return word_norm[0] + restore_hamza(word_norm[1:], 0, r1_orig)
            return word_norm

        elif pattern_type == 'imperative':
            return word_norm[-2:] if len(word_norm) >= 2 else word_norm

        elif pattern_type == 'agent':
            # Handle important cases: أاكل / ااكل → آكل (only for مهموز الفاء + فاعل)
            if len(word_norm) >= 2:
                if (word_norm.startswith('أا') or word_norm.startswith('اا')) and r1_orig == 'أ':
                    return 'آ' + word_norm[2:]

            return word_norm

        elif pattern_type == 'patient':
            # مفعول → مأكول: hamza as first root letter (after م)
            if len(word_norm) >= 2:
                return word_norm[0] + r1_orig + word_norm[2:]
            return word_norm
    
    # === 1.6. مهموز العين (Hamza at MIDDLE) ===
    if verb_type == "مهموز العين":
        if pattern_type == 'past':
            # فَأَعَلَ - restore hamza at position 1
            return restore_hamza(word_norm, 1, r2_orig)
        elif pattern_type == 'present':
            # يَفْأَعَلُ - restore hamza at position 2 (after ي + first consonant)
            if word_norm.startswith('ي'):
                return word_norm[0:2] + restore_hamza(word_norm[2:], 0, r2_orig)
            return word_norm
        elif pattern_type == 'imperative':
            # اِفْأَعَلْ - restore hamza at position 1 (after ا + first consonant)
            if word_norm.startswith('ا'):
                return word_norm[0:2] + restore_hamza(word_norm[2:], 0, r2_orig)
            return word_norm
        elif pattern_type == 'agent':
            # Fix مهموز العين in فاعل: ساأل / ساال → سائل
            # Rule: ا + (ء or normalized ا from hamza) → ائ
            if len(word_norm) >= 3:
                # Case 1: normalized form (ساال)
                if word_norm[1] == 'ا' and word_norm[2] == 'ا':
                    return word_norm[0] + 'ائ' + word_norm[3:]
                # Case 2: original root has hamza as عين (سأل، قرأ، ملأ)
                if word_norm[1] == 'ا' and root[1] in ['ء', 'أ', 'إ', 'آ']:
                    return word_norm[0] + 'ائ' + word_norm[3:]
            return word_norm
        else:  # patient
            # مَفْؤُول - hamza in position 2
            return word_norm[:2] + restore_hamza(word_norm[2:], 0, r2_orig) if len(word_norm) >= 3 else word_norm
    
    # === 1.7. مهموز اللام (Hamza at END) ===
    if verb_type == "مهموز اللام":
        # All patterns: keep word_norm and restore hamza at end
        if pattern_type in ['past', 'present', 'imperative', 'patient']:
            # Restore hamza at last position
            return restore_hamza(word_norm, len(word_norm) - 1, r3_orig)
        return word_norm
    
    # === 2. مثال واوي (Weak at START: و) ===
    # Patterns: وَفَعَلَ | يَفْعِلُ | فِعْلْ | فَاعِل | مَفْعُول
    if verb_type == "مثال واوي":
        if pattern_type == 'past':
            # Keep: وَفَعَلَ (weak و at start)
            return word_norm
        elif pattern_type == 'present':
            # يَفْعِلُ (drop و, keep ي from pattern)
            # Pattern gives يَوْعَد, should drop و → يعد
            if len(word_norm) >= 2 and word_norm[1] in ['و', 'ي']:
                return word_norm[0] + word_norm[2:]
            return word_norm
        elif pattern_type == 'imperative':
            # فِعْلْ (drop ا prefix AND weak و)
            # Pattern gives افْعَل, word is اوعد
            # Result: عد (remove ا and و)
            if len(word_norm) >= 3 and word_norm[0] == 'ا' and word_norm[1] in ['و', 'ي']:
                return word_norm[2:]
            elif len(word_norm) >= 2 and word_norm[1] in ['و', 'ي']:
                return word_norm[0] + word_norm[2:]
            return word_norm
        else:  # agent, patient
            return word_norm
    
    # === 2.1. مثال يائي (Weak at START: ي) ===
    # Patterns: يَفْعَلَ | يَفْعَلُ | اِفْعَلْ | فَاعِل | مَفْعُول
    if verb_type == "مثال يائي":
        if pattern_type == 'past':
            # Keep: يَفْعَلَ (ي at start, but not counted as weak in classical sense)
            return word_norm
        elif pattern_type == 'present':
            # يَفْعَلُ (normal present)
            return word_norm
        elif pattern_type == 'imperative':
            # اِفْعَلْ (normal imperative with ا prefix)
            return word_norm
        else:  # agent, patient
            return word_norm
    
    # === 3. أجوف واوي (Weak in MIDDLE: و) ===
    # Patterns: فَالَ | يَفُولُ | فُلْ | فَائِل | مَفُول
    if verb_type == "أجوف واوي":
        if pattern_type == 'past':
            # فَالَ (keep و as alef في الماضي)
            return word_norm
        elif pattern_type == 'present':
            # يَفُولُ (damma becomes و in present)
            return word_norm
        elif pattern_type == 'imperative':
            # فُلْ (just ف + ل, no ا prefix, و becomes damma before ل)
            # Pattern gives اقال, should be قل (first and last letter only)
            if len(word_norm) >= 2:
                return word_norm[0] + word_norm[-1]
            return word_norm
        elif pattern_type == 'agent':
            # فَائِل (ا + ي + ل, with hamza)
            if 'ال' in word_norm or 'او' in word_norm:
                word_norm = word_norm.replace('ال', 'ائ').replace('او', 'ائ')
            return word_norm
        elif pattern_type == 'patient':
            # مَفُول (keep و)
            return word_norm
    
    # === 3.1. أجوف يائي (Weak in MIDDLE: ي) ===
    # Patterns: فَالَ | يَفِيلُ | فِلْ | فَائِل | مَفِيل
    if verb_type == "أجوف يائي":
        if pattern_type == 'past':
            # فَالَ (ي as alef في الماضي)
            return word_norm
        elif pattern_type == 'present':
            # يَفِيلُ (ي with kasra)
            return word_norm
        elif pattern_type == 'imperative':
            # فِلْ (just ف + ل, with kasra, no ا prefix)
            # Pattern gives اقال, should be قل (first and last letter only)
            if len(word_norm) >= 2:
                return word_norm[0] + word_norm[-1]
            return word_norm
        elif pattern_type == 'agent':
            # فَائِل (ا + ي + ل, with hamza)
            if 'ال' in word_norm or 'اي' in word_norm:
                word_norm = word_norm.replace('ال', 'ائ').replace('اي', 'ائ')
            return word_norm
        elif pattern_type == 'patient':
            # مَفِيل (ي in patient)
            return word_norm
    
    # === 4. ناقص واوي (Weak at END: و) ===
    # Patterns: فَعَا | يَفْعُو | اِفْعُ | فَاعٍ | مَفْعُوّ
    if verb_type == "ناقص واوي":
        if pattern_type == 'past':
            # فَعَا (ا from pattern, و from root)
            return word_norm
        elif pattern_type == 'present':
            # يَفْعُو (damma before و)
            return word_norm
        elif pattern_type == 'imperative':
            # اِفْعُ (drop weak end)
            # Pattern gives افعا, should drop ا → افع
            if word_norm.endswith('ا') or word_norm.endswith('و') or word_norm.endswith('ي'):
                return word_norm[:-1]
            return word_norm
        elif pattern_type == 'agent':
            # ناقص واوي في فاعل: دعا → داعي (لا نحذف الحرف الأخير)
            return word_norm
        elif pattern_type == 'patient':
            # مدعو (remove extra و if duplicated at end)
            if word_norm.endswith('وو'):
                return word_norm[:-1]
            return fix_naqis_patient(word_norm, root)
    
    # === 4.1. ناقص يائي (Weak at END: ي/ى) ===
    # Patterns: فَعَى | يَفْعِي | اِفْعِ | فَاعٍ | مَفْعِيّ
    if verb_type == "ناقص يائي":
        if pattern_type == 'past':
            # فَعَى (ا from pattern becomes ى)
            return word_norm
        elif pattern_type == 'present':
            # يَفْعِي (ي with kasra)
            return word_norm
        elif pattern_type == 'imperative':
            # اِفْعِ (drop weak end)
            # Pattern gives افعي, should drop ي → افع
            if word_norm.endswith('ا') or word_norm.endswith('و') or word_norm.endswith('ي'):
                return word_norm[:-1]
            return word_norm
        elif pattern_type == 'agent':
            # ناقص يائي في اسم الفاعل: بقي → باقي (لا نحذف الحرف الأخير)
            return word_norm
        elif pattern_type == 'patient':
            # مبقوي → مبقي (remove inserted و before last root letter)
            return fix_naqis_patient(word_norm, root)
    
    # ===  4.2. ناقص ألفي (Weak at END: ا) ===
    if verb_type == "ناقص ألفي":
        if pattern_type == 'past':
            # Keep ا
            return word_norm
        elif pattern_type == 'present':
            # Keep ا or convert
            return word_norm
        elif pattern_type == 'imperative':
            # Drop weak end
            if word_norm.endswith('ا') or word_norm.endswith('و') or word_norm.endswith('ي'):
                return word_norm[:-1]
            return word_norm
        elif pattern_type == 'agent':
            # ناقص ألفي في اسم الفاعل: دعا → داعي (ا → ي)
            if word_norm.endswith('ا'):
                return word_norm[:-1] + 'ي'
            return word_norm
        elif pattern_type == 'patient':
            # ناقص ألفي: دعا → مدعو ، رمى → مرمي
            # 1) Drop final weak ا/ي
            if word_norm.endswith(('ا', 'ي')):
                word_norm = word_norm[:-1]
            # 2) Ensure it ends with و
            if not word_norm.endswith('و'):
                word_norm += 'و'
            return word_norm
    
    # === 5. لفيف مفروق (Weak at START + END, separated) ===
    if verb_type == "لفيف مفروق":
        if pattern_type == 'past':
            return word_norm
        elif pattern_type == 'present':
            return word_norm
        elif pattern_type == 'imperative':
            # لفيف مفروق في الأمر: نحذف الأول والآخر ونبقي العين فقط (وقى → ق)
            if len(root) == 3:
                return root[1]
            return word_norm
        elif pattern_type == 'agent':
            # لفيف مفروق في اسم الفاعل: وقى → واقٍ
            if len(word_norm) >= 2 and root[2] in ['و', 'ي', 'ى']:
                return word_norm[:-1] + 'ٍ'
            return word_norm
        else:  # patient
            return word_norm
    
    # === 6. لفيف مقرون واوي (Weak at START: و + END: ي) ===
    # Patterns: فَوَى | يَفْوِي | اِفْوِ | فَاوٍ | مَفْوِيّ
    if verb_type == "لفيف مقرون واوي":
        if pattern_type == 'past':
            # فَوَى (keep و and ي as ا)
            return word_norm
        elif pattern_type == 'present':
            # يَفْوِي (و with fatha, ي with kasra)
            return word_norm
        elif pattern_type == 'imperative':
            # اِفْوِ (drop ي from end, keep و)
            # Pattern gives افوي, should be افو or فو
            if word_norm.endswith('ي') or word_norm.endswith('ا'):
                return word_norm[:-1]
            return word_norm
        elif pattern_type == 'agent':
            # لفيف مقرون واوي في اسم الفاعل: طاوي → طاوٍ
            if word_norm.endswith("وي"):
                return word_norm[:-1] + "ٍ"
            return word_norm
        elif pattern_type == 'patient':
            # مَفْوِيّ (و + ي with doubled ي)
            return word_norm
    
    # === 6.1. لفيف مقرون يائي (Weak at START: ي + END: ي) ===
    # Patterns: فَيَى | يَفْيِي | اِفْيِ | فَايٍ | مَفْيِيّ
    if verb_type == "لفيف مقرون يائي":
        if pattern_type == 'past':
            # فَيَى (keep ي twice, second becomes ا)
            return word_norm
        elif pattern_type == 'present':
            # يَفْيِي (both ي with kasra)
            return word_norm
        elif pattern_type == 'imperative':
            # اِفْيِ (keep both ي)
            # Pattern gives افيي, already correct
            return word_norm
        elif pattern_type == 'agent':
            # فَايٍ (ي + ي with nunation)
            return word_norm
        elif pattern_type == 'patient':
            # مَفْيِيّ (ي + ي with doubled ي)
            return word_norm
    
    # === DEFAULT: Return normalized word ===
    return word_norm


# --- Irregular Verb Rules (I'Lal & Ibdal) from verb_rules.txt ---

VERB_RULES_TXT_FILE = "data/verb_rules.txt"
_IRREGULAR_RULES: Dict[str, List[tuple]] = {}  # key -> [(op, args), ...]

def _verb_type_to_rule_prefix(verb_type: str) -> Optional[str]:
    """Map verb type to rule key prefix (mithal, ajwaf, naqis, lafif, mahmouz, sahih)."""
    if not verb_type:
        return None
    if "مثال" in verb_type:
        return "mithal"
    if "أجوف" in verb_type:
        return "ajwaf"
    if "ناقص" in verb_type:
        return "naqis"
    if "لفيف" in verb_type:
        return "lafif"
    if "مهموز" in verb_type:
        return "mahmouz"
    if "صحيح" in verb_type or "مضاعف" in verb_type:
        return "sahih"
    return None


def _load_irregular_rules():
    """Load and parse verb_rules.txt into _IRREGULAR_RULES."""
    global _IRREGULAR_RULES
    _IRREGULAR_RULES = {}
    if not os.path.exists(VERB_RULES_TXT_FILE):
        return
    try:
        with open(VERB_RULES_TXT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" not in line:
                    continue
                key, ops_str = line.split(":", 1)
                key = key.strip()
                ops = []
                for op in ops_str.split(";"):
                    op = op.strip()
                    if not op:
                        continue
                    # Ignore malformed ops that start with '=' (e.g. '=طاو')
                    if op.startswith("="):
                        continue
                    if op.startswith("replace="):
                        # replace=A>B (B may be empty, e.g. replace=او>)
                        part = op[8:].strip()
                        if ">" in part:
                            a, b = part.split(">", 1)
                            a = a.strip()
                            b = b.strip()
                            # Skip empty source (replace=>X would corrupt everything)
                            if a:
                                ops.append(("replace", (a, b)))
                    elif op.startswith("replace_final="):
                        # replace_final=B
                        b = op[13:].strip()
                        ops.append(("replace_final", (b,)))
                # Store even empty ops (e.g. sahih_يفعل: = no change)
                _IRREGULAR_RULES[key] = ops
    except Exception as e:
        print(f"Error loading verb_rules.txt: {e}")


def _apply_irregular_rules(word: str, root: str, verb_type: str, scheme_id: str) -> str:
    """
    Apply irregular verb rules from verb_rules.txt.
    Order: 1) exception_{root}_{pattern}, 2) {type}_{pattern}, 3) default (no change).
    Called after apply_verb_transformations.
    """
    if not word:
        return word

    # Skip irregular rules for لفيف مفروق + فاعل (اسم الفاعل يعالج في المنطق الأساسي)
    if verb_type == "لفيف مفروق" and scheme_id == "فاعل":
        return word

    # 1. Exception first (e.g. exception_قال_فاعل, exception_باع_مفعول)
    exc_key = f"exception_{root}_{scheme_id}"
    if exc_key in _IRREGULAR_RULES:
        for op, args in _IRREGULAR_RULES[exc_key]:
            if op == "replace":
                a, b = args
                if a:
                    word = word.replace(a, b)
            elif op == "replace_final" and len(word) >= 1:
                word = word[:-1] + args[0]
        return word

    # 2. Apply verb-type + scheme rules
    prefix = _verb_type_to_rule_prefix(verb_type)
    if not prefix:
        return word

    rule_key = f"{prefix}_{scheme_id}"
    if rule_key not in _IRREGULAR_RULES:
        return word

    for op, args in _IRREGULAR_RULES[rule_key]:
        if op == "replace":
            a, b = args
            if a:
                word = word.replace(a, b)
        elif op == "replace_final" and len(word) >= 1:
            word = word[:-1] + args[0]

    return word


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
_load_irregular_rules()

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
    
    verb_type = root_data.verb_type
    word = apply_pattern(root, scheme.pattern, verb_type)
    
    # Apply verb-specific transformations (pass pattern and scheme_id for context)
    word = apply_verb_transformations(word, root, verb_type, scheme.pattern, scheme_id)
    # Apply irregular verb rules from verb_rules.txt (I'Lal & Ibdal)
    word = _apply_irregular_rules(word, root, verb_type, scheme_id)
    # Final safety: strip stray '=' from rule parsing glitches
    word = word.replace("=", "").strip()
    
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
    verb_type = root_data.verb_type or ""
    
    found_scheme = None
    for s in schemes:
        generated = apply_pattern(root_str, s.pattern, verb_type)
        generated = apply_verb_transformations(generated, root_str, verb_type, s.pattern, s.id)
        generated = _apply_irregular_rules(generated, root_str, verb_type, s.id)
        generated = generated.replace("=", "").strip()
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
