from collections import deque, defaultdict
from typing import List, Dict, Tuple, Any

    ## @class Node
    ## @brief Representasi sebuah node dalam automaton Aho-Corasick.
class AhoCorasick:
    def __init__(self):
        self.name = "Aho-Corasick"
        self._automaton_cache: Dict[Tuple[str, ...], Any] = {}
        
    class Node:
        def __init__(self):
            self.children = {}
            self.failure = None
            self.output = []
            
    # @brief Membangun automaton Aho-Corasick dari sekumpulan pola.
    # @param patterns: List pola (string) yang akan dimasukkan ke dalam automaton.
    # @return: Root node dari automaton yang telah dibangun.
    def build_automaton(self, patterns):
        patterns_tuple = tuple(sorted(p.lower() for p in patterns))
        if patterns_tuple in self._automaton_cache:
            return self._automaton_cache[patterns_tuple] 
        
        root = self.Node()
        
        # Membangun trie
        for i, pattern in enumerate(patterns):
            node = root
            pattern_lower = pattern.lower()
            
            for char in pattern_lower:
                if char not in node.children:
                    node.children[char] = self.Node()
                node = node.children[char]
            
            node.output.append((i, pattern))

        # Membangun failure links menggunakan BFS
        queue = deque()

        # Inisialisasi failure links untuk anak-anak root
        for char, child in root.children.items():
            child.failure = root
            queue.append(child)

        # BFS untuk membangun failure links
        while queue:
            current = queue.popleft()
            
            for char, child in current.children.items():
                queue.append(child)
                
                # Cari failure link untuk child
                failure = current.failure
                while failure and char not in failure.children:
                    failure = failure.failure
                
                if failure:
                    child.failure = failure.children[char]
                else:
                    child.failure = root
                
                # Gabungin output dari failure link ke child
                if child.failure:
                    child.output.extend(child.failure.output)
        
        # Simpan ke cache
        self._automaton_cache[patterns_tuple] = root
        return root
    
    # @brief Mencari satu pola dalam teks (untuk kompatibilitas dengan algoritma lain).
    # @param text: Teks yang akan dicari.
    # @param pattern: Pola tunggal yang akan dicocokkan.
    # @return: List berisi posisi di mana pola ditemukan.
    def search(self, text, pattern):
        results = self.search_multiple(text, [pattern])
        if pattern in results:
            return results[pattern]['positions']
        return []
    
    # @brief Fungsi utama untuk mencari beberapa pola sekaligus secara efisien.
    # @param text: Teks yang akan dicari.
    # @param patterns: List pola yang akan dicocokkan.
    # @return: Dictionary yang isinya <pola, <'positions', 'count'>>. Kalau kosong ya kosong.
    def search_multiple(self, text, patterns):
        if not text or not patterns:
            return {}        
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
    
    # @brief Menghitung jumlah kemunculan sebuah pola dalam teks.
    # @param text: Teks yang akan dicari.
    # @param pattern: Pola yang akan dihitung.
    # @return: Jumlah kemunculan pola (integer).
    def count_occurrences(self, text, pattern):
        return len(self.search(text, pattern))
    
    # @brief Alias untuk search_multiple untuk menekankan keunggulan Aho-Corasick.
    # @param text: Teks yang akan dicari.
    # @param patterns: List pola yang akan dicocokkan.
    # @return: Hasil dari search_multiple.
    def search_all_patterns(self, text, patterns):
        return self.search_multiple(text, patterns)