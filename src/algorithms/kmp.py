class KMP:
    def __init__(self):
        self.name = "Knuth-Morris-Pratt"
    
    def compute_lps(self, pattern):
        """Compute Longest Prefix Suffix array"""
        m = len(pattern)
        lps = [0] * m
        length = 0
        i = 1
        
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
    
    def search(self, text, pattern):
        """
        Search for pattern in text using KMP algorithm
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
        
        lps = self.compute_lps(pattern_lower)
        positions = []
        
        i = 0  # index for text
        j = 0  # index for pattern
        
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