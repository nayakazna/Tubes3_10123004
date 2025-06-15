##########################################################################
##########################################################################
## @file boyer_moore.py
## Ini isinya implementasi algoritma Boyer-Moore (BM)
##########################################################################
##########################################################################

from typing import List, Tuple, Dict, Any

class BoyerMoore:
    def __init__(self):
        self.name = "Boyer-Moore"
        self._pattern_cache = {} # biar gak recompute yg udh ada
    

    # @brief Menghitung tabel 'bad character' untuk pergeseranAdd commentMore actions
    # @param pattern: Pola string yang akan dianalisis
    # @return: Tabel (list) yang memetakan setiap karakter ke posisi terakhirnya dalam pola
    def _bad_char_heuristic(self, pattern: str) -> list[int]:
        bad_char = [-1] * 256  # ascii table
        for i in range(len(pattern)):
            bad_char[ord(pattern[i])] = i
            
        return bad_char
    
    # @brief Menghitung tabel 'good suffix' untuk pergeseran yang lebih optimalAdd commentMore actions
    # @param pattern: Pola string yang akan diproses
    # @return: Tabel (list) yang berisi jarak pergeseran berdasarkan sufiks yang cocok
    def _good_suffix_heuristic(self, pattern: str) -> list[int]:
        m: int = len(pattern)
        suffix: list[int] = [0] * m
        good_suffix: list[int] = [m] * m
        
        # Compute suffix array
        suffix[m - 1] = m
        g: int = m - 1
        f: int = m - 1
        
        for i in range(m - 2, -1, -1):
            if i > g and suffix[i + m - 1 - f] < i - g:
                suffix[i] = suffix[i + m - 1 - f]
            else:
                if i < g:
                    g = i
                f = i
                while g >= 0 and pattern[g] == pattern[g + m - 1 - f]:
                    g -= 1
                suffix[i] = f - g

        # kasus 1: good suffix pernah muncul
        for i in range(m-1):
            good_suffix[m - 1 - suffix[i]] = m - 1 - i
            
        # kasus 2: yang pernah muncul cuma prefix dari good suffix sbg suffix pattern
        j: int = 0
        for i in range(m - 1, -1, -1):
            if suffix[i] == i + 1:
                while j < m - 1 - i:
                    if good_suffix[j] == m:
                        good_suffix[j] = m - 1 - i
                    j += 1
                    
        for i in range(m - 1):
            good_suffix[m - 1 - suffix[i]] = m - 1 - i
            
        return good_suffix
    
    # @brief Melakukan pra-pemrosesan pola dengan menghitung tabel bad char & good suffixAdd commentMore actions
    # @details Mengecek cache dulu, kalau polanya sudah pernah diproses, langsung kembalikan hasilnya biar gak recompute.
    # @param pattern: Pola yang akan diproses
    # @return: Tuple yang isinya tabel bad character dan tabel good suffix
    def preprocess_pattern(self, pattern: str) -> tuple[list[int], list[int]]:
        pattern_key = (pattern, len(pattern))
        
        if pattern_key in self._pattern_cache:
            return self._pattern_cache[pattern_key]
        
        bad_char = self._bad_char_heuristic(pattern)
        good_suffix = self._good_suffix_heuristic(pattern)
        
        self._pattern_cache[pattern_key] = (bad_char, good_suffix)
        return bad_char, good_suffix


    # @brief fungsi utama untuk algoritma Boyer-Moore
    # @param text: Teks yang akan dicariAdd commentMore actions
    # @param pattern: Pola yang akan dicocokkan
    # @return: List berisi semua posisi awal ditemukannya pola, kalau gaada ya kosong
    def search(self, text: str, pattern: str) -> list[int]:
        if not text or not pattern or len(pattern) > len(text):
            return []
        text_l = text.lower()
        pat_l  = pattern.lower()
        bad, good = self.preprocess_pattern(pat_l)

        n, m = len(text_l), len(pat_l)
        res = []
        s = 0
        bad_local = bad
        good_local = good
        txt = text_l
        pat = pat_l

        while s <= n - m:
            j = m - 1
            # skip re‑matching a known good suffix? (Galil rule) …
            while j >= 0 and pat[j] == txt[s + j]:
                j -= 1
            if j < 0:
                res.append(s)
                s += good_local[0]  # or incorporate Galil
            else:
                bc = bad_local[ord(txt[s+j])] if ord(txt[s+j]) < len(bad_local) else -1
                shift1 = j - bc if bc >= 0 else j + 1
                shift2 = good_local[j]
                s += shift1 if shift1 > shift2 else shift2
        return res

    # @brief Mencari kemunculan pertama dari pola dalam teks
    # @param text: Teks yang akan dicariAdd commentMore actions
    # @param pattern: Pola yang akan dicocokkan
    # @return: Posisi awal kemunculan pertama pola, atau -1 kalau gaada
    def search_first(self, text: str, pattern: str) -> int:
        n: int = len(text)
        m: int = len(pattern)
        if m > n:
            return -1
        
        bad_char, good_suffix = self._preprocess_pattern(pattern)

        s: int = 0
        while s <= n - m:
            j: int = m - 1
            
            while j >= 0 and pattern[j] == text[s + j]:
                j -= 1
                
            if j < 0:
                return s  # kemunculan pertama
                
            char_code = ord(text[s + j])
            shift = bad_char[char_code] if char_code < len(bad_char) else -1
            bad_char_shift = max(1, j - shift)
            good_suffix_shift = good_suffix[j]
            s += max(bad_char_shift, good_suffix_shift)
            return -1

    # @brief Menghitung jumlah kemunculan pola dalam teksAdd commentMore actions
    # @param text: Teks yang akan dicari
    # @param pattern: Pola yang akan dicocokkan
    # @return: Jumlah total kemunculan pola
    def count_occurrences(self, text: str, pattern: str) -> int:
        return len(self.search(text, pattern))
    
    # @brief Mencari beberapa pola sekaligus dalam satu teks
    # @param text: Teks yang akan dicariAdd commentMore actions
    # @param patterns: List berisi pola-pola yang mau dicari
    # @return: Dictionary yang isinya hasil pencarian, bentuknya pola -> {posisi, jumlah}
    def search_multiple(self, text: str, patterns: List[str]) -> Dict[str, Dict[str, Any]]:
        results = {}
        
        text = text.lower()
        
        for pattern in patterns:
            positions = self.search(text, pattern)
            if positions:
                results[pattern] = {
                    'positions': positions,
                    'count': len(positions)
                }
        return results
    
    def clear_cache(self):
        self._pattern_cache.clear()