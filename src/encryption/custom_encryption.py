import base64

class CustomEncryption:
    """
    Custom encryption implementation without using built-in encryption libraries.
    This uses a combination of Caesar cipher, XOR, and custom substitution.
    """
    
    def __init__(self, key="ATS2025SecretKey"):
        self.key = key
        self.shift = sum(ord(c) for c in key) % 26
        
        # Create substitution table
        self.substitution_table = self._create_substitution_table()
        self.reverse_table = {v: k for k, v in self.substitution_table.items()}
        
    def _create_substitution_table(self):
        """Create a custom substitution table based on the key"""
        import string
        
        # All possible characters
        chars = string.ascii_letters + string.digits + string.punctuation + ' '
        
        # Create a shuffled version based on key
        shuffled = list(chars)
        
        # Use key to shuffle - more deterministic approach
        import random
        random.seed(self.key)
        random.shuffle(shuffled)
        
        return dict(zip(chars, shuffled))
    
    def _caesar_cipher(self, text, decrypt=False):
        """Apply Caesar cipher"""
        result = []
        shift = -self.shift if decrypt else self.shift
        
        for char in text:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                shifted = chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
                result.append(shifted)
            else:
                result.append(char)
                
        return ''.join(result)
    
    def _xor_cipher(self, text):
        """Apply XOR cipher with key - simplified version"""
        result = []
        key_length = len(self.key)
        
        for i, char in enumerate(text):
            key_char = self.key[i % key_length]
            # Simple XOR without constraining to printable range
            xor_result = ord(char) ^ ord(key_char)
            result.append(xor_result)
            
        return result
    
    def _reverse_xor_cipher(self, data):
        """Reverse XOR cipher"""
        result = []
        key_length = len(self.key)
        
        for i, byte_val in enumerate(data):
            key_char = self.key[i % key_length]
            # XOR is its own inverse
            original = byte_val ^ ord(key_char)
            result.append(chr(original))
            
        return ''.join(result)
    
    def _substitution_cipher(self, text, decrypt=False):
        """Apply substitution cipher"""
        table = self.reverse_table if decrypt else self.substitution_table
        result = []
        
        for char in text:
            if char in table:
                result.append(table[char])
            else:
                # Keep characters not in table as-is
                result.append(char)
                
        return ''.join(result)
    
    def encrypt(self, plaintext):
        """
        Encrypt text using multiple cipher layers:
        1. Caesar cipher
        2. Substitution cipher
        3. XOR cipher
        4. Base64 encoding for safe storage
        """
        if not plaintext:
            return ""
            
        # Layer 1: Caesar cipher
        step1 = self._caesar_cipher(plaintext)
        
        # Layer 2: Substitution cipher
        step2 = self._substitution_cipher(step1)
        
        # Layer 3: XOR cipher (returns list of integers)
        step3 = self._xor_cipher(step2)
        
        # Convert to bytes and encode with base64 for safe storage
        bytes_data = bytes(step3)
        encrypted = base64.b64encode(bytes_data).decode('utf-8')
        
        return encrypted
    
    def decrypt(self, ciphertext):
        """
        Decrypt text by reversing the encryption layers
        """
        if not ciphertext:
            return ""
            
        try:
            # Decode from base64
            bytes_data = base64.b64decode(ciphertext.encode('utf-8'))
            
            # Convert bytes back to list of integers
            xor_data = list(bytes_data)
            
            # Reverse Layer 3: XOR cipher
            step1 = self._reverse_xor_cipher(xor_data)
            
            # Reverse Layer 2: Substitution cipher
            step2 = self._substitution_cipher(step1, decrypt=True)
            
            # Reverse Layer 1: Caesar cipher
            decrypted = self._caesar_cipher(step2, decrypt=True)
            
            return decrypted
            
        except Exception as e:
            print(f"Decryption error: {e}")
            return ""
    
    def encrypt_profile_data(self, profile_dict):
        """Encrypt sensitive fields in profile dictionary"""
        encrypted_profile = profile_dict.copy()
        
        # Fields to encrypt
        sensitive_fields = ['first_name', 'last_name', 'address', 'phone_number']
        
        for field in sensitive_fields:
            if field in encrypted_profile and encrypted_profile[field]:
                encrypted_profile[field] = self.encrypt(str(encrypted_profile[field]))
                
        return encrypted_profile
    
    def decrypt_profile_data(self, encrypted_dict):
        """Decrypt sensitive fields in profile dictionary"""
        decrypted_profile = encrypted_dict.copy()
        
        # Fields to decrypt
        sensitive_fields = ['first_name', 'last_name', 'address', 'phone_number']
        
        for field in sensitive_fields:
            if field in decrypted_profile and decrypted_profile[field]:
                decrypted_profile[field] = self.decrypt(str(decrypted_profile[field]))
                
        return decrypted_profile