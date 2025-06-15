##########################################################################
##########################################################################
## @file kmp.py
## Ini isinya implementasi algoritma Knuth-Morris-Pratt (KMP)
##########################################################################
##########################################################################

from typing import List, Dict

class KMP:
    def __init__(self, cache_limit: int = 1000):
        self.name = "KMP"
        self._lps_cache: Dict[str, List[int]] = {}
        self._cache_limit = cache_limit
        self._cache_access_count = {}

    def _evict_cache(self) -> None:
        if len(self._lps_cache) >= self._cache_limit:
            lru_pattern = min(self._cache_access_count.items(), key=lambda x: x[1])[0]
            del self._lps_cache[lru_pattern]
            del self._cache_access_count[lru_pattern]

    # @brief Menghitung Longest Prefix Suffix array dari pola
    # @param pattern: Pola yang dipakai untuk pattern matching
    # @return: LPS array yang berisi panjang prefix yang juga suffix untuk setiap indeks
    def _compute_lps(self, pattern: str) -> List[int]:
        if pattern in self._lps_cache:
            self._cache_access_count[pattern] += 1
            return self._lps_cache[pattern]

        m: int = len(pattern)
        if m == 0:
            return []
        if m == 1:
            lps: List[int] = [0]
        else:
            lps: List[int] = [0] * m
            length: int = 0
            i: int = 1
            while i < m:
                if pattern[i] == pattern[length]:
                    length += 1
                    lps[i] = length
                    i += 1
                else:
                    if length != 0:
                        length = lps[length - 1]
                    else:
                        lps[i] = 0
                        i += 1
        self._evict_cache()
        self._lps_cache[pattern] = lps
        self._cache_access_count[pattern] = 1
        return lps
    
    # @brief fungsi utama untuk algoritma KMP
    # @param text: Teks yang akan dicari
    # @param pattern: Pola yang akan dicocokkan
    # @return: List posisi di mana pola ditemukan dalam teks, kalau gaada ya kosong
    def search(self, text: str, pattern: str, is_lowercase: bool = False) -> List[int]:
        if not text or not pattern:
            return []
            
        n: int = len(text)
        m: int = len(pattern)
        
        if m > n:
            return []
        
        # prep
        text: str = text.lower() if is_lowercase else text
        pattern: str = pattern.lower()
        positions: list[int] = []

        # ambil dari cache atau hitung baru
        lps: List[int] = self._compute_lps(pattern)

        i: int = 0  # index untuk teks
        j: int = 0  # index untuk pola

        while i < n:
            if text[i] == pattern[j]:
                i += 1
                j += 1
                
                if j == m:
                    positions.append(i - m)
                    j = lps[j - 1]
            else:
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1
        return positions

    # @brief Mencari beberapa pola dalam teks
    # @param text: Teks yang akan dicari
    # @param patterns: List pola yang akan dicocokkan
    # @return: Dictionary yang bentuknya kayak <pola, <posisi, count>>
    def search_multiple(self, text: str, patterns: list[str]) -> dict[str, dict[str, int]]:
        if not text or not patterns:
            return {}
        
        results: dict[str, dict[str, int]] = {}
        text = text.lower()
        for pattern in patterns:
            positions = self.search(text, pattern, is_lowercase=True)
            if positions:
                results[pattern] = {
                    'positions': positions,
                    'count': len(positions)
                }
        return results

    # @brief membersihkan cache LPS
    # @return: None
    def clear_cache(self):
        self._lps_cache.clear()
    