import base64

class CustomEncryption:
    # Enkripsi pake beberapa lapisan:
    # 1. Caesar cipher
    # 2. Substitution cipher
    # 3. XOR cipher
    # 4. Base64 encoding for safe storage (makanya ada akhiran == klo diliat di db)    
    def __init__(self, key="ATS2025SecretKey"):
        self.key = key
        self.shift = sum(ord(c) for c in key) % 26
        
        self.substitution_table = self._create_substitution_table()
        self.reverse_table = {v: k for k, v in self.substitution_table.items()}
        
    def _create_substitution_table(self):
        import string
        
        chars = string.ascii_letters + string.digits + string.punctuation + ' '
        shuffled = list(chars)

        import random
        random.seed(self.key)
        random.shuffle(shuffled)
        
        return dict(zip(chars, shuffled))
    
    def _caesar_cipher(self, text, decrypt=False):
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
        result = []
        key_length = len(self.key)
        
        for i, char in enumerate(text):
            key_char = self.key[i % key_length]
            # Simple XOR without constraining to printable range
            xor_result = ord(char) ^ ord(key_char)
            result.append(xor_result)
            
        return result
    
    def _reverse_xor_cipher(self, data):
        result = []
        key_length = len(self.key)
        
        for i, byte_val in enumerate(data):
            key_char = self.key[i % key_length]
            original = byte_val ^ ord(key_char)
            result.append(chr(original))
            
        return ''.join(result)
    
    def _substitution_cipher(self, text, decrypt=False):
        table = self.reverse_table if decrypt else self.substitution_table
        result = []
        
        for char in text:
            if char in table:
                result.append(table[char])
            else:
                result.append(char)
                
        return ''.join(result)
    
    def encrypt(self, plaintext):
        if not plaintext:
            return ""
            
        # Layer 1: Caesar cipher
        step1 = self._caesar_cipher(plaintext)
        
        # Layer 2: Substitution cipher
        step2 = self._substitution_cipher(step1)
        
        # Layer 3: XOR cipher
        step3 = self._xor_cipher(step2)
        
        # Convert ke bytes, pake base64 encoding
        bytes_data = bytes(step3)
        encrypted = base64.b64encode(bytes_data).decode('utf-8')
        
        return encrypted
    
    def decrypt(self, ciphertext):
        if not ciphertext:
            return ""
            
        try:
            bytes_data = base64.b64decode(ciphertext.encode('utf-8'))
            xor_data = list(bytes_data)
            step1 = self._reverse_xor_cipher(xor_data)
            step2 = self._substitution_cipher(step1, decrypt=True)
            decrypted = self._caesar_cipher(step2, decrypt=True)
            return decrypted
            
        except Exception as e:
            print(f"Decryption error: {e}")
            return ""
    
    def encrypt_profile_data(self, profile_dict):
        encrypted_profile = profile_dict.copy()
        
        sensitive_fields = ['first_name', 'last_name', 'address', 'phone_number']
        
        for field in sensitive_fields:
            if field in encrypted_profile and encrypted_profile[field]:
                encrypted_profile[field] = self.encrypt(str(encrypted_profile[field]))
                
        return encrypted_profile
    
    def decrypt_profile_data(self, encrypted_dict):
        decrypted_profile = encrypted_dict.copy()
        sensitive_fields = ['first_name', 'last_name', 'address', 'phone_number']
        
        for field in sensitive_fields:
            if field in decrypted_profile and decrypted_profile[field]:
                decrypted_profile[field] = self.decrypt(str(decrypted_profile[field]))
                
        return decrypted_profile