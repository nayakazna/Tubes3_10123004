##########################################################################
##########################################################################
## @file kmp.py
## Ini isinya implementasi algoritma Knuth-Morris-Pratt (KMP)
## Dioptimize berdasarkan paper ini:
## https://iopscience.iop.org/article/10.1088/1742-6596/1345/4/042005/pdf
## NB: aku tambahin docs biar rapi ya rel
##########################################################################
##########################################################################

class KMP:
    def __init__(self):
        self.name = "KMP"

    # @brief Menghitung Longest Prefix Suffix array dari pola
    # @param pattern: Pola yang dipakai untuk pattern matching
    # @return: LPS array yang berisi panjang prefix yang juga suffix untuk setiap indeks
    def _compute_lps(self, pattern: str) -> list[int]:
        m: int = len(pattern)
        lps: list[int] = [0] * m
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
        return lps
    
    # @brief fungsi utama untuk algoritma KMP
    # @param text: Teks yang akan dicari
    # @param pattern: Pola yang akan dicocokkan
    # @return: List posisi di mana pola ditemukan dalam teks, kalau gaada ya kosong
    def search(self, text: str, pattern: str, is_lowercase: bool = False) -> list[int]:
        if not text or not pattern:
            return []
            
        n: int = len(text)
        m: int = len(pattern)
        
        if m > n:
            return []
        
        # prep
        text_lower: str = text.lower() if is_lowercase else text
        pattern_lower: str = pattern.lower()
        lps: list[int] = self._compute_lps(pattern_lower)
        positions: list[int] = []

        i: int = 0  # index untuk teks
        j: int = 0  # index untuk pola

        while i < n:
            if text_lower[i] == pattern_lower[j]:
                i += 1
                j += 1
                
            if j == m:
                positions.append(i - j)
                j = lps[j - 1]
            elif i < n and text_lower[i] != pattern_lower[j]:
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