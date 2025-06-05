from collections import deque, defaultdict

class AhoCorasick:
    def __init__(self):
        self.name = "Aho-Corasick"
        
    class Node:
        def __init__(self):
            self.children = {}
            self.failure = None
            self.output = []
            
    def build_automaton(self, patterns):
        """Build Aho-Corasick automaton from patterns"""
        root = self.Node()
        
        # Build trie
        for i, pattern in enumerate(patterns):
            node = root
            pattern_lower = pattern.lower()
            
            for char in pattern_lower:
                if char not in node.children:
                    node.children[char] = self.Node()
                node = node.children[char]
            
            node.output.append((i, pattern))
        
        # Build failure links using BFS
        queue = deque()
        
        # Initialize failure links for root's children
        for char, child in root.children.items():
            child.failure = root
            queue.append(child)
        
        # BFS to build failure links
        while queue:
            current = queue.popleft()
            
            for char, child in current.children.items():
                queue.append(child)
                
                # Find failure link
                failure = current.failure
                while failure and char not in failure.children:
                    failure = failure.failure
                
                if failure:
                    child.failure = failure.children[char]
                else:
                    child.failure = root
                
                # Merge output from failure link
                if child.failure:
                    child.output.extend(child.failure.output)
        
        return root
    
    def search(self, text, pattern):
        """
        Search for single pattern in text (for compatibility with other algorithms)
        """
        results = self.search_multiple(text, [pattern])
        if pattern in results:
            return results[pattern]['positions']
        return []
    
    def search_multiple(self, text, patterns):
        """
        Search for multiple patterns in text using Aho-Corasick
        Returns dictionary with pattern as key and list of positions as value
        """
        if not text or not patterns:
            return {}
        
        # Build automaton
        root = self.build_automaton(patterns)
        
        # Search in text
        results = defaultdict(lambda: {'positions': [], 'count': 0})
        text_lower = text.lower()
        current = root
        
        for i, char in enumerate(text_lower):
            # Follow failure links until we find a match or reach root
            while current and char not in current.children:
                current = current.failure
            
            if current:
                current = current.children[char]
            else:
                current = root
            
            # Check all patterns that end at current position
            for pattern_idx, pattern in current.output:
                start_pos = i - len(pattern) + 1
                results[pattern]['positions'].append(start_pos)
                results[pattern]['count'] += 1
        
        # Convert defaultdict to regular dict and filter empty results
        return {k: v for k, v in results.items() if v['positions']}
    
    def count_occurrences(self, text, pattern):
        """Count occurrences of pattern in text"""
        return len(self.search(text, pattern))
    
    def search_all_patterns(self, text, patterns):
        """
        Efficiently search for all patterns simultaneously
        This is the main advantage of Aho-Corasick over KMP/BM
        """
        return self.search_multiple(text, patterns)