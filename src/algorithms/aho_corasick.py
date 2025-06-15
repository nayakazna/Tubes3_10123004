from collections import deque, defaultdict
from typing import List, Dict, Tuple, Any

    ## @brief Representasi sebuah node dalam automaton Aho-Corasick.
class AhoCorasick:
    def __init__(self):
        self.name = "Aho-Corasick"
        self._automaton_cache: Dict[frozenset, Any] = {}
        
    class Node:
        __slots__ = ['children', 'failure', 'output']
        def __init__(self):
            self.children = {}
            self.failure = None
            self.output = []
            
    # @brief Membangun automaton Aho-Corasick dari sekumpulan pola.
    # @param patterns: List pola (string) yang akan dimasukkan ke dalam automaton.
    # @return: Root node dari automaton yang telah dibangun.
    def build_automaton(self, patterns: List[str]) -> Node:
        if not patterns:
            return None
        
        # cache key
        patterns_key = frozenset(p.lower() for p in patterns)
        if patterns_key in self._automaton_cache:
            return self._automaton_cache[patterns_key]

        # konversi pola ke tuple untuk menghindari masalah mutable types
        lower_to_original = {}
        for pattern in set(patterns):
            lower = pattern.lower()
            if lower not in lower_to_original:
                lower_to_original[lower] = pattern  
        
        root = self.Node()
        
        # Membangun trie
        for i, (lower, original) in enumerate(lower_to_original.items()):
            node = root
            for char in lower:
                if char not in node.children:
                    node.children[char] = self.Node()
                node = node.children[char]
            node.output.append((i, original))

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
                f = current.failure
                while f and char not in f.children:
                    f = f.failure

                child.failure = f.children[char] if f and char in f.children else root
                
                # Gabungin output dari failure link ke child
                child.output = list(dict.fromkeys(child.output + child.failure.output))
        
        # Simpan ke cache
        self._automaton_cache[patterns_key] = root
        return root
    
    # @brief Mencari satu pola dalam teks (untuk kompatibilitas dengan algoritma lain).
    # @param text: Teks yang akan dicari.
    # @param pattern: Pola tunggal yang akan dicocokkan.
    # @return: List berisi posisi di mana pola ditemukan.
    def search(self, text: str, pattern: str) -> List[int]:
        results = self.search_multiple(text, [pattern])
        if pattern in results:
            return results[pattern]['positions']
        return []
    
    # @brief Fungsi utama untuk mencari beberapa pola sekaligus secara efisien.
    # @param text: Teks yang akan dicari.
    # @param patterns: List pola yang akan dicocokkan.
    # @return: Dictionary yang isinya <pola, <'positions', 'count'>>. Kalau kosong ya kosong.
    def search_multiple(self, text: str, patterns: List[str], root=None) -> Dict[str, Dict[str, Any]]:
        if not text or not patterns:
            return {}        
        
        if root is None:
            root = self.build_automaton(patterns)
        if root is None:
            return {}
        
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
            for _, pattern in current.output:
                start_pos = i - len(pattern) + 1
                results[pattern]['positions'].append(start_pos)
                results[pattern]['count'] += 1
        
        # Convert defaultdict to regular dict and filter empty results
        return {k: v for k, v in results.items() if v['positions']}
    
    # @brief Menghitung jumlah kemunculan sebuah pola dalam teks.
    # @param text: Teks yang akan dicari.
    # @param pattern: Pola yang akan dihitung.
    # @return: Jumlah kemunculan pola (integer).
    def count_occurrences(self, text: str, pattern: str) -> int:
        return len(self.search(text, pattern))
    
    # @brief Alias untuk search_multiple untuk menekankan keunggulan Aho-Corasick.
    # @param text: Teks yang akan dicari.
    # @param patterns: List pola yang akan dicocokkan.
    # @return: Hasil dari search_multiple.
    def search_all_patterns(self, text: str, patterns: List[str]) -> Dict[str, Dict[str, Any]]:
        return self.search_multiple(text, patterns)