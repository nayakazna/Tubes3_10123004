##########################################################################
##########################################################################
## @file boyer_moore.py
## Ini isinya implementasi algoritma Boyer-Moore (BM)
##########################################################################
##########################################################################

from typing import List, Tuple

class BoyerMoore:
    def __init__(self):
        self.name = "Boyer-Moore"
        self._pattern_cache = {} # biar gak recompute yg udh ada
    
    # @brief Menghitung tabel 'bad character' untuk pergeseran
    # @param pattern: Pola string yang akan dianalisis
    # @return: Tabel (list) yang memetakan setiap karakter ke posisi terakhirnya dalam pola
    def _bad_char_heuristic(self, pattern: str) -> list[int]:
        bad_char = [-1] * 256  # ascii table
        for i in range(len(pattern)):
            bad_char[ord(pattern[i])] = i
            
        return bad_char
    
    # @brief Menghitung tabel 'good suffix' untuk pergeseran yang lebih optimal
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

        # kasus 1: yang pernah muncul cuma prefix dari good suffix sbg suffix pattern
        j: int = 0
        for i in range(m - 1, -1, -1):
            if suffix[i] == i + 1:
                while j < m - 1 - i:
                    if good_suffix[j] == m:
                        good_suffix[j] = m - 1 - i
                    j += 1
                    
        # kasus 2: good suffix pernah muncul
        for i in range(m - 1):
            good_suffix[m - 1 - suffix[i]] = m - 1 - i
            
        return good_suffix
    
    # @brief Melakukan pra-pemrosesan pola dengan menghitung tabel bad char & good suffix
    # @details Mengecek cache dulu, kalau polanya sudah pernah diproses, langsung kembalikan hasilnya biar gak recompute.
    # @param pattern: Pola yang akan diproses
    # @return: Tuple yang isinya tabel bad character dan tabel good suffix
    def _preprocess_pattern(self, pattern: str) -> tuple[list[int], list[int]]:
        pattern_key = (pattern, len(pattern))
        
        if pattern_key in self._pattern_cache:
            return self._pattern_cache[pattern_key]
        
        bad_char = self._bad_char_heuristic(pattern)
        good_suffix = self._good_suffix_heuristic(pattern)
        
        self._pattern_cache[pattern_key] = (bad_char, good_suffix)
        return bad_char, good_suffix

    # @brief fungsi utama untuk algoritma Boyer-Moore
    # @param text: Teks yang akan dicari
    # @param pattern: Pola yang akan dicocokkan
    # @return: List berisi semua posisi awal ditemukannya pola, kalau gaada ya kosong
    def search(self, text: str, pattern: str) -> list[int]:
        if not text or not pattern:
            return []

        n: int = len(text)
        m: int = len(pattern)

        if m > n:
            return []
        
        # Convert to lowercase for case-insensitive search
        text: str = text.lower()
        pattern: str = pattern.lower()

        # ambil preprocessing atau hitung baru
        bad_char, good_suffix = self._preprocess_pattern(pattern)

        positions = []
        s: int = 0  # shift of pattern with respect to text

        while s <= n - m:
            j = m - 1
            
            # Keep reducing index j while characters match
            while j >= 0 and pattern[j] == text[s + j]:
                j -= 1
                
            if j < 0:
                # Pattern found
                positions.append(s)
                
                # Shift pattern using good suffix heuristic
                s += good_suffix[0] if s + m < n else 1
            else:
                # Shift pattern using max of bad char and good suffix
                bad_char_shift = max(1, j - bad_char[ord(text[s + j])])
                good_suffix_shift = good_suffix[j]
                s += max(bad_char_shift, good_suffix_shift)
        return positions

    # @brief Mencari kemunculan pertama dari pola dalam teks
    # @param text: Teks yang akan dicari
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
                
            bad_char_shift = max(1, j - bad_char[ord(text[s + j])])
            good_suffix_shift = good_suffix[j]
            s += max(bad_char_shift, good_suffix_shift)
            return -1
    
    # @brief Menghitung jumlah kemunculan pola dalam teks
    # @param text: Teks yang akan dicari
    # @param pattern: Pola yang akan dicocokkan
    # @return: Jumlah total kemunculan pola
    def count_occurrences(self, text: str, pattern: str) -> int:
        return len(self.search(text, pattern))
    
    # @brief Mencari beberapa pola sekaligus dalam satu teks
    # @param text: Teks yang akan dicari
    # @param patterns: List berisi pola-pola yang mau dicari
    # @return: Dictionary yang isinya hasil pencarian, bentuknya pola -> {posisi, jumlah}
    def search_multiple(self, text, patterns):
        """
        Search for multiple patterns in text
        Returns dictionary with pattern as key and list of positions as value
        """
        results = {}
        for pattern in patterns:
            text = text.lower()
            pattern = pattern.lower()
            positions = self.search(text, pattern)
            if positions:
                results[pattern] = {
                    'positions': positions,
                    'count': len(positions)
                }
        return results
    
    def clear_cache(self):
        self._pattern_cache.clear()