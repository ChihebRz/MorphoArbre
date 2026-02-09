
/**
 * Arabic Morphological Logic
 * Root components: ف (1st), ع (2nd), ل (3rd)
 */

export function generateWord(root: string, pattern: string): string {
  if (root.length !== 3) return "Error: Root must be 3 characters";
  
  const r1 = root[0];
  const r2 = root[1];
  const r3 = root[2];

  // We replace 'ف', 'ع', 'ل' in the pattern with the root characters.
  // Note: Modern Arabic patterns might have diacritics (harakat).
  // This logic preserves harakat attached to the characters.
  
  let result = "";
  for (let char of pattern) {
    if (char === 'ف') result += r1;
    else if (char === 'ع') result += r2;
    else if (char === 'ل') result += r3;
    else result += char;
  }
  
  return result;
}

export function validateWord(word: string, root: string, patterns: string[]): { isValid: boolean; scheme?: string } {
  for (const pattern of patterns) {
    const generated = generateWord(root, pattern);
    // Simple equality check, ideally would handle diacritics normalization
    if (normalizeArabic(generated) === normalizeArabic(word)) {
      return { isValid: true, scheme: pattern };
    }
  }
  return { isValid: false };
}

/**
 * Basic normalization to help with matching
 */
function normalizeArabic(text: string): string {
  return text
    .replace(/[\u064B-\u0652]/g, "") // Remove harakat
    .replace(/آ/g, "ا")
    .replace(/إ/g, "ا")
    .replace(/أ/g, "ا")
    .replace(/ؤ/g, "و")
    .replace(/ئ/g, "ي")
    .replace(/ة/g, "ه");
}

export function decomposeWord(word: string, patterns: string[]): { root: string; scheme: string } | null {
  // Advanced decomposition logic would require reverse-mapping.
  // For this mini-project, we'll iterate through known patterns and try to extract 3 consonants.
  // This is a simplified approach.
  return null; 
}
