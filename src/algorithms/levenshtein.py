##########################################################################
##########################################################################
## @file levenshtein.py
## Ini isinya implementasi algoritma Levenshtein Distance untuk
## pencarian fuzzy (fuzzy string matching).
##########################################################################
##########################################################################

import re
from collections import defaultdict
from typing import List, Dict, Tuple, Any

class LevenshteinDistance:
    def __init__(self, threshold=0.8):
        self.threshold = threshold  # Similarity threshold (0.8 = 80% similar)
    
    # @brief Menghitung jarak Levenshtein antara dua string.
    # @param s1: String pertama.
    # @param s2: String kedua.
    # @return: Jarak Levenshtein (integer) antara s1 dan s2.
    def calculate_distance(self, s1, s2):
        if not s1:
            return len(s2)
        if not s2:
            return len(s1)
        
        # Convert to lowercase for case-insensitive comparison
        s1 = s1.lower()
        s2 = s2.lower()
        m, n = len(s1), len(s2)
        
        if m < n:
            return self.calculate_distance(s2, s1)  # biar efisien

        # skrg amanh m >= n
        prev_row = list(range(n + 1))
        for i in range(1, m + 1):
            curr_row = [i] * (n + 1)
            for j in range(1, n + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                curr_row[j] = min(
                    curr_row[j - 1] + 1,  # Insertion
                    prev_row[j] + 1,      # Deletion
                    prev_row[j - 1] + cost # Substitution
                )
            prev_row = curr_row
        return prev_row[n]
    
    # @brief Menghitung persentase kemiripan antara dua string.
    # @param s1: String pertama.
    # @param s2: String kedua.
    # @return: Skor kemiripan (float) antara 0.0 dan 1.0.
    def calculate_similarity(self, s1, s2):
        if not s1 and not s2:
            return 1.0
        
        distance = self.calculate_distance(s1, s2)
        max_len = max(len(s1), len(s2))
        
        if max_len == 0:
            return 1.0
        
        similarity = 1 - (distance / max_len)
        return similarity
    
    # @brief Melakukan pencarian fuzzy untuk beberapa kata kunci sekaligus.
    # @param text: Teks sumber untuk pencarian.
    # @param keywords: List kata kunci yang akan dicari.
    # @param min_similarity: Ambang batas kemiripan minimum.
    # @return: Dictionary yang key-nya adalah kata kunci dan value-nya list kata-kata mirip yang ditemukan.
    def fuzzy_search(self, text, keywords, min_similarity=None):
        if min_similarity is None:
            min_similarity = self.threshold
        
        results = defaultdict(list)
        
        # tokenisasi + pembersihan teks
        tokenized_words = [{'word': match.group(0), 'position': match.start()} for match in re.finditer(r'\b\w+\b', text)]

        for keyword in keywords:
            keyword = keyword.lower()
            for token in tokenized_words:
                similarity = self.calculate_similarity(token['word'], keyword)
                if similarity >= min_similarity:
                    if keyword not in results:
                        results[keyword] = []
                    results[keyword].append({
                        'word': token['word'],
                        'similarity': similarity,
                        'position': token['position']
                    })
        return results
    
    # @brief Mengatur nilai ambang batas kemiripan.
    # @param threshold: Nilai ambang batas baru (antara 0.0 dan 1.0).
    # @return: None.
    def set_threshold(self, threshold):
        if 0.0 <= threshold <= 1.0:
            self.threshold = threshold
        else:
            raise ValueError("Threshold must be between 0.0 and 1.0")