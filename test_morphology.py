#!/usr/bin/env python3
"""
Test morphological transformations for all 7 verb types.
Based on the comprehensive Arabic morphology guide.
"""

import sys
import requests
import json

BASE_URL = "http://localhost:8000"

# Test cases: (root, verb_type, [(scheme_id, expected_output_pattern)])
TEST_CASES = [
    # 1. صحيح سالم (Regular) - كتب
    {
        "root": "كتب",
        "verb_type": "صحيح سالم",
        "tests": [
            ("فعل", "كتب"),        # ماضي: فَعَلَ
            ("يفعل", "يكتب"),      # مضارع: يَفْعَلُ
            ("أمر", "اكتب"),       # أمر: اِفْعَلْ
            ("فاعل", "كاتب"),      # اسم الفاعل: فَاعِل
            ("مفعول", "مكتوب"),    # اسم المفعول: مَفْعُول
        ]
    },
    
    # 2. مثال واوي (Weak at start: و) - وجد
    {
        "root": "وجد",
        "verb_type": "مثال واوي",
        "tests": [
            ("فعل", "وجد"),        # ماضي: وَفَعَلَ (keeps و)
            ("يفعل", "يجد"),       # مضارع: يَفْعِلُ (drops و)
            ("أمر", "جد"),         # أمر: فِعْل (drops و)
            ("فاعل", "واجد"),      # اسم الفاعل: وَافِعِل (keeps و)
            ("مفعول", "موجود"),    # اسم المفعول: مَوْفُوع (keeps م + و)
        ]
    },
    
    # 3. أجوف واوي (Weak at middle: و) - قال
    {
        "root": "قال",
        "verb_type": "أجوف واوي",
        "tests": [
            ("فعل", "قال"),       # ماضي: فَالَ (ع=و becomes ا)
            ("يفعل", "يقول"),     # مضارع: يَفُولُ (weak و returns)
            ("أمر", "قل"),        # أمر: فُلْ (short form)
            ("فاعل", "قائل"),     # اسم الفاعل: فَائِل (ا+ا→ائ)
            ("مفعول", "مقول"),    # اسم المفعول: مَفُول (keeps و from pattern)
        ]
    },
    
    # 4. ناقص يائي (Weak at end: ي/ى) - بقي
    {
        "root": "بقي",
        "verb_type": "ناقص يائي",
        "tests": [
            ("فعل", "بقي"),       # ماضي: فَعَا (original ا)
            ("يفعل", "يبقى"),     # مضارع: يَفْعُو (ي→ى, و from pattern)
            ("أمر", "ابق"),       # أمر: اِفْعُ (drops final ي)
            ("فاعل", "باق"),      # اسم الفاعل: فَاعٍ (drops ي)
            ("مفعول", "مبقوي"),   # اسم المفعول: مَفْعُوّ (keeps و+ي)
        ]
    },
    
    # 5. ناقص واوي (Weak at end: ا/و) - دعا
    {
        "root": "دعا",
        "verb_type": "ناقص واوي",
        "tests": [
            ("فعل", "دعا"),       # ماضي: فَعَا
            ("يفعل", "يدعو"),     # مضارع: يَفْعُو (ا→و)
            ("أمر", "ادع"),       # أمر: اِفْعُ (drops ا)
            ("فاعل", "داع"),      # اسم الفاعل: فَاعٍ (drops ا)
            ("مفعول", "مدعو"),    # اسم المفعول: مَفْعُول (ا→و)
        ]
    },
    
    # 6. لفيف مفروق (Weak at start AND end) - وقى
    {
        "root": "وقى",
        "verb_type": "لفيف مفروق",
        "tests": [
            ("فعل", "وقى"),       # ماضي: وَفَعَا
            ("يفعل", "يقي"),      # مضارع: يَفْعِي (drops initial و)
            ("أمر", "قي"),        # أمر: فِ (very short)
            ("فاعل", "واق"),      # اسم الفاعل: وَافٍ (drops final ي)
            ("مفعول", "موقي"),    # اسم المفعول: مَوْفِيّ
        ]
    },
    
    # 7. لفيف مقرون (Weak at middle AND end) - طوى
    {
        "root": "طوى",
        "verb_type": "لفيف مقرون",
        "tests": [
            ("فعل", "طوى"),       # ماضي: فَوَى
            ("يفعل", "يطوي"),     # مضارع: يَفْوِي
            ("أمر", "اطو"),       # أمر: اِفْوِ
            ("فاعل", "طاو"),      # اسم الفاعل: فَاوٍ (drops final ي)
            ("مفعول", "مطوي"),    # اسم المفعول: مَفْوِيّ
        ]
    },
    
    # Bonus: مضاعف (Doubled) - مدد
    {
        "root": "مدد",
        "verb_type": "مضاعف",
        "tests": [
            ("فعل", "مدد"),       # ماضي: فَعَّ
            ("يفعل", "يمدد"),     # مضارع: يَفَعُّ
            ("أمر", "امدد"),      # أمر: فَعَّ
            ("فاعل", "مادد"),     # اسم الفاعل: فَاعّ
            ("مفعول", "ممدود"),   # اسم المفعول: مَفْعُول
        ]
    },
    
    # مهموز الفاء (Hamza at start) - أكل
    {
        "root": "أكل",
        "verb_type": "مهموز الفاء",
        "tests": [
            ("فعل", "أكل"),       # ماضي: فَعَلَ
            ("يفعل", "يأكل"),     # مضارع: يَفْعَلُ
            ("أمر", "اكل"),       # أمر: اِفْعَلْ (drops hamza)
            ("فاعل", "آكل"),      # اسم الفاعل: فَاعِل (ا+ا→آ)
            ("مفعول", "ماكول"),   # اسم المفعول: مَفْعُول
        ]
    },
]

def normalize_for_comparison(text: str) -> str:
    """Normalize text for comparison (remove diacritics, standardize alefs)."""
    import re
    text = re.sub(r'[\u064B-\u0652]', '', text)  # Remove harakat
    text = text.replace('آ', 'ا')
    text = text.replace('أ', 'ا')
    text = text.replace('إ', 'ا')
    text = text.replace('ى', 'ي')
    return text.strip()

def test_generation():
    """Test word generation for all verb types."""
    print("\n" + "="*80)
    print("🧪 TESTING MORPHOLOGICAL TRANSFORMATIONS")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for test_group in TEST_CASES:
        root = test_group["root"]
        verb_type = test_group["verb_type"]
        
        print(f"\n📌 Testing: {root} ({verb_type})")
        print("-" * 60)
        
        for scheme_id, expected_pattern in test_group["tests"]:
            try:
                # Call API to generate
                response = requests.post(
                    f"{BASE_URL}/api/generate",
                    params={"root": root, "scheme_id": scheme_id}
                )
                
                if response.status_code != 200:
                    print(f"  ❌ {scheme_id:10} | API Error: {response.status_code}")
                    failed += 1
                    continue
                
                result = response.json()
                generated_word = result.get("word", "")
                
                # Normalize both for comparison
                gen_norm = normalize_for_comparison(generated_word)
                exp_norm = normalize_for_comparison(expected_pattern)
                
                # Check if match
                if gen_norm == exp_norm:
                    print(f"  ✅ {scheme_id:10} | {generated_word:15} (expected pattern: {expected_pattern})")
                    passed += 1
                else:
                    print(f"  ❌ {scheme_id:10} | Got: {generated_word:15} Expected: {expected_pattern}")
                    failed += 1
                    
            except Exception as e:
                print(f"  ❌ {scheme_id:10} | Exception: {str(e)}")
                failed += 1
    
    print("\n" + "="*80)
    print(f"📊 RESULTS: {passed} passed, {failed} failed out of {passed + failed}")
    print("="*80)
    
    return failed == 0

if __name__ == "__main__":
    success = test_generation()
    sys.exit(0 if success else 1)
