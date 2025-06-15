##########################################################################
##########################################################################
## @file levenshtein.py
## Ini isinya implementasi algoritma Levenshtein Distance untuk
## pencarian fuzzy (fuzzy string matching).
##########################################################################
##########################################################################

import re
from collections import defaultdict
from typing import List, Dict, Tuple, Any, Optional

class LevenshteinDistance:
    def __init__(self, threshold: int =0.65, cache_limit: int = 1000):
        self.threshold = threshold  # Similarity threshold (0.7 = 70% similar)
        self._distance_cache = {}  # Cache untuk menghindari perhitungan berulang
        self.cache_limit = 1000
        self._word_cleaner =  re.compile(r'[^\w\s]', re.UNICODE)
        self._whitespace = re.compile(r'\s+')
        
    def _evict_cache(self):
        if len(self._distance_cache) >= self.cache_limit:
            lru_key = min(self._distance_cache.keys(), key=lambda k: self._distance_cache[k][1])
            del self._distance_cache[lru_key]

    # @brief Menghitung jarak Levenshtein antara dua string.
    # @param s1: String pertama.
    # @param s2: String kedua.
    # @return: Jarak Levenshtein (integer) antara s1 dan s2.
    def calculate_distance(self, s1, s2, max_distance: Optional[int] = None):
        if not s1:
            return len(s2)
        if not s2:
            return len(s1)
        if s1 == s2:
            return 0

        # Convert to lowercase for case-insensitive comparison
        s1 = s1.lower()
        s2 = s2.lower()
        m, n = len(s1), len(s2)
        
        # cek cache
        cache_key = (s1, s2, max_distance)
        if cache_key in self._distance_cache:
            return self._distance_cache[cache_key]

        # biar efisien, kalau panjang s1 < s2, tukar aja
        if m < n:
            return self.calculate_distance(s2, s1) 

        # skrg amanh m >= n
        prev_row = list(range(n + 1))
        curr_row = [0] * (n + 1)
        
        for i in range(1, m + 1):
            curr_row[0] = i
            diagonal_min = float('inf')
            
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    curr_row[j] = prev_row[j-1]
                else:
                    curr_row[j] = 1 + min(
                        prev_row[j],     # deletion
                        curr_row[j-1],   # insertion
                        prev_row[j-1]    # substitution
                    )
                
                diagonal_min = min(diagonal_min, curr_row[j])
            
            if max_distance is not None and diagonal_min > max_distance:
                return max_distance + 1
            
            # Swap rows
            prev_row, curr_row = curr_row, prev_row
        
        # Simpan hasil ke cache
        self._evict_cache()
        self._distance_cache[cache_key] = prev_row[n]
        return prev_row[n]
    
    # @brief Menghitung persentase kemiripan antara dua string.
    # @param s1: String pertama.
    # @param s2: String kedua.
    # @return: Skor kemiripan (float) antara 0.0 dan 1.0.
    def calculate_similarity(self, s1, s2):
        if not s1 and not s2:
            return 1.0
        
        max_len = max(len(s1), len(s2))
        max_distance = int(max_len * (1 - self.threshold)) + 1
        distance = self.calculate_distance(s1, s2, max_distance)
        
        if max_len == 0:
            return 1.0
        
        similarity = 1 - (distance / max_len)
        return similarity
    
    # @brief Melakukan pencarian fuzzy untuk beberapa kata kunci sekaligus.
    # @param text: Teks sumber untuk pencarian.
    # @param keywords: List kata kunci yang akan dicari.
    # @param min_similarity: Ambang batas kemiripan minimum.
    # @return: Dictionary yang key-nya adalah kata kunci dan value-nya list kata-kata mirip yang ditemukan.
    def fuzzy_search(self, text: str, keywords: List[str], min_similarity: float = None) -> Dict[str, List[Dict[str, Any]]]:
        if min_similarity is None:
            min_similarity = self.threshold

        results = defaultdict(list)
        
        # preprocessing
        processed_keywords = [(kw.lower(), len(kw.split())) for kw in keywords]

        # token
        word_matches = list(re.finditer(r'\b[\w#+.-]+\b', text))
        words = [m.group(0) for m in word_matches]
        positions = [m.start() for m in word_matches]

        # Buat token windows untuk setiap kata kunci
        max_kw_len = max(length for _, length in processed_keywords)
        
        token_windows = []
        for window_size in range(1, max_kw_len + 1):
            for i in range(len(words) - window_size + 1):
                phrase = ' '.join(words[i:i + window_size])
                token_windows.append({
                    'word': phrase,
                    'position': positions[i]
                })

        # cache untuk menghindari perhitungan berulang
        similarity_cache = {}

        for keyword, kw_len in processed_keywords:
            for token in token_windows:
                key_pair = (token['word'], keyword)
                if key_pair in similarity_cache:
                    similarity = similarity_cache[key_pair]
                else:
                    similarity = self.calculate_similarity(token['word'], keyword)
                    similarity_cache[key_pair] = similarity

                if similarity >= min_similarity:
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
        

# test driver
if __name__ == "__main__":
    import time
    ld = LevenshteinDistance()
    print(f"threshold: {ld.threshold}\n")

    # Contoh 1: Typo sederhana (substitusi)
    s1, s2 = "python", "pyhton"
    distance1 = ld.calculate_distance(s1, s2)
    similarity1 = ld.calculate_similarity(s1, s2)
    print(f"Jarak antara '{s1}' dan '{s2}': {distance1}")
    print(f"Tingkat kemiripan: {similarity1:.2f}\n")

    # Contoh 2: Perbedaan panjang (insersi/delesi)
    s3, s4 = "java", "javascript"
    distance2 = ld.calculate_distance(s3, s4)
    similarity2 = ld.calculate_similarity(s3, s4)
    print(f"Jarak antara '{s3}' dan '{s4}': {distance2}")
    print(f"Tingkat kemiripan: {similarity2:.2f}\n")


    # 3. Uji coba kasus penggunaan utama: fuzzy_search
    # Ini adalah skenario yang paling relevan untuk aplikasi ATS Anda.
    print("--- 2. Uji Coba fuzzy_search pada Teks CV ---")
    
    sample_cv_text = """
    Nama: NAYAKA
    Pengalaman: Software Engineer dengan fokus pada pyhton dan pengembangan web.
    Mahir dalam Java, Javascript, dan C++. Mencari posisi sebagai 'project manager'.
    Saya juga pernah mengerjakan proyek dengan nod.js.
    """
    
    keywords_to_find = ["python", "java", "node.js", "project management", "C#"]
    
    print(f"Teks CV yang akan dipindai:\n---\n{sample_cv_text.strip()}\n---\n")
    print(f"Kata kunci yang dicari: {keywords_to_find}")
    print(f"Threshold kemiripan yang digunakan: {ld.threshold}")
    print("\n>>> Hasil Pencarian Fuzzy:")

    # Panggil metode fuzzy_search yang sudah dioptimalkan
    # (menggunakan re.finditer untuk mendapatkan posisi)
    start_time = time.time()
    fuzzy_results = ld.fuzzy_search(sample_cv_text, keywords_to_find)
    end_time = time.time()
    print(f"\nWaktu eksekusi: {end_time - start_time:.4f} detik\n")
    if not fuzzy_results:
        print("Tidak ada kata yang mirip ditemukan.")
    else:
        # Cetak hasilnya dengan rapi
        for keyword, matches in fuzzy_results.items():
            print(f"\n  Kata Kunci '{keyword}' ditemukan mirip dengan:")
            for match in matches:
                print(
                    f"    - Kata: '{match['word']}' "
                    f"(Kemiripan: {match['similarity']:.2f}, "
                    f"Posisi: {match['position']})"
                )
    
