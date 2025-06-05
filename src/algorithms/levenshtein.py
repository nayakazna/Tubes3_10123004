class LevenshteinDistance:
    def __init__(self, threshold=0.8):
        self.threshold = threshold  # Similarity threshold (0.8 = 80% similar)
    
    def calculate_distance(self, s1, s2):
        """Calculate Levenshtein distance between two strings"""
        if not s1:
            return len(s2)
        if not s2:
            return len(s1)
        
        # Convert to lowercase for case-insensitive comparison
        s1 = s1.lower()
        s2 = s2.lower()
        
        # Create distance matrix
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Initialize base cases
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        # Fill the matrix
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i-1][j],    # deletion
                        dp[i][j-1],    # insertion
                        dp[i-1][j-1]   # substitution
                    )
        
        return dp[m][n]
    
    def calculate_similarity(self, s1, s2):
        """Calculate similarity percentage between two strings"""
        if not s1 and not s2:
            return 1.0
        
        distance = self.calculate_distance(s1, s2)
        max_len = max(len(s1), len(s2))
        
        if max_len == 0:
            return 1.0
        
        similarity = 1 - (distance / max_len)
        return similarity
    
    def find_similar_words(self, text, keyword, min_similarity=None):
        """
        Find words in text that are similar to keyword
        Returns list of (word, similarity_score, position) tuples
        """
        if min_similarity is None:
            min_similarity = self.threshold
        
        # Split text into words
        words = text.split()
        similar_words = []
        
        position = 0
        for word in words:
            # Clean word (remove punctuation)
            cleaned_word = ''.join(c for c in word if c.isalnum())
            
            if cleaned_word:
                similarity = self.calculate_similarity(cleaned_word, keyword)
                
                if similarity >= min_similarity:
                    # Find position in original text
                    word_position = text.find(word, position)
                    similar_words.append({
                        'word': cleaned_word,
                        'similarity': similarity,
                        'position': word_position
                    })
                
                position = text.find(word, position) + len(word)
        
        return similar_words
    
    def fuzzy_search(self, text, keywords, min_similarity=None):
        """
        Perform fuzzy search for multiple keywords
        Returns dictionary with keyword as key and list of similar words as value
        """
        if min_similarity is None:
            min_similarity = self.threshold
        
        results = {}
        
        for keyword in keywords:
            similar = self.find_similar_words(text, keyword, min_similarity)
            if similar:
                results[keyword] = similar
        
        return results
    
    def set_threshold(self, threshold):
        """Set similarity threshold (0.0 to 1.0)"""
        if 0.0 <= threshold <= 1.0:
            self.threshold = threshold
        else:
            raise ValueError("Threshold must be between 0.0 and 1.0")