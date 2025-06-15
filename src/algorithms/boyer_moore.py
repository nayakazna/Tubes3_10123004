class BoyerMoore:
    def __init__(self):
        self.name = "Boyer-Moore"
        self._pattern_cache = {} # biar gak recompute yg udh ada
    
    def _bad_char_heuristic(self, pattern: str) -> list[int]:
        bad_char = [-1] * 256  # ascii table
        for i in range(len(pattern)):
            bad_char[ord(pattern[i])] = i
            
        return bad_char
    
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
    
    def _preprocess_pattern(self, pattern: str) -> tuple[list[int], list[int]]:
        pattern_key = (pattern, len(pattern))
        
        if pattern_key in self._pattern_cache:
            return self._pattern_cache[pattern_key]
        
        bad_char = self._bad_char_heuristic(pattern)
        good_suffix = self._good_suffix_heuristic(pattern)
        
        self._pattern_cache[pattern_key] = (bad_char, good_suffix)
        return bad_char, good_suffix

    def search(self, text: str, pattern: str) -> list[int]:
        if not text or not pattern or len(pattern) > len(text):
            return []
        text_l = text.lower()
        pat_l  = pattern.lower()
        bad, good = self._preprocess_pattern(pat_l)

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

    def count_occurrences(self, text: str, pattern: str) -> int:
        return len(self.search(text, pattern))
    
    def search_multiple(self, text, patterns):
        """
        Search for multiple patterns in text
        Returns dictionary with pattern as key and list of positions as value
        """
        results = {}
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