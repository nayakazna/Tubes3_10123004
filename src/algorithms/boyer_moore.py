class BoyerMoore:
    def __init__(self):
        self.name = "Boyer-Moore"
    
    def bad_char_heuristic(self, pattern):
        """Create bad character heuristic table"""
        bad_char = {}
        
        for i in range(len(pattern)):
            bad_char[pattern[i]] = i
            
        return bad_char
    
    def good_suffix_heuristic(self, pattern):
        """Create good suffix heuristic table"""
        m = len(pattern)
        good_suffix = [0] * m
        
        # Helper arrays
        suffix = [0] * m
        
        # Compute suffix array
        suffix[m - 1] = m
        g = m - 1
        
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
        
        # Compute good suffix table
        for i in range(m):
            good_suffix[i] = m
            
        j = 0
        for i in range(m - 1, -1, -1):
            if suffix[i] == i + 1:
                while j < m - 1 - i:
                    if good_suffix[j] == m:
                        good_suffix[j] = m - 1 - i
                    j += 1
                    
        for i in range(m - 1):
            good_suffix[m - 1 - suffix[i]] = m - 1 - i
            
        return good_suffix
    
    def search(self, text, pattern):
        """
        Search for pattern in text using Boyer-Moore algorithm
        Returns list of starting indices where pattern is found
        """
        if not text or not pattern:
            return []
            
        n = len(text)
        m = len(pattern)
        
        if m > n:
            return []
        
        # Convert to lowercase for case-insensitive search
        text_lower = text.lower()
        pattern_lower = pattern.lower()
        
        # Preprocessing
        bad_char = self.bad_char_heuristic(pattern_lower)
        good_suffix = self.good_suffix_heuristic(pattern_lower)
        
        positions = []
        s = 0  # shift of pattern with respect to text
        
        while s <= n - m:
            j = m - 1
            
            # Keep reducing index j while characters match
            while j >= 0 and pattern_lower[j] == text_lower[s + j]:
                j -= 1
                
            if j < 0:
                # Pattern found
                positions.append(s)
                
                # Shift pattern using good suffix heuristic
                s += good_suffix[0] if s + m < n else 1
            else:
                # Shift pattern using max of bad char and good suffix
                bad_char_shift = j - bad_char.get(text_lower[s + j], -1)
                good_suffix_shift = good_suffix[j]
                s += max(bad_char_shift, good_suffix_shift)
        
        return positions
    
    def count_occurrences(self, text, pattern):
        """Count occurrences of pattern in text"""
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