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
    def __init__(self, threshold=0.65):
        self.threshold = threshold  # Similarity threshold (0.7 = 70% similar)
    
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
    
