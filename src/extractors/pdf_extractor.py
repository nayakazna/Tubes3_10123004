import PyPDF2
import os
import sys
from datetime import datetime

class PDFExtractor:
    def __init__(self):
        self.extracted_texts = {}
        self.show_progress = True
        self.debug_mode = True
        
    def save_debug(self, filename, content, pdf_name=""):
        if self.debug_mode:
            debug_dir = "debug_pdf_extraction"
            os.makedirs(debug_dir, exist_ok=True)
            
            if pdf_name:
                base, ext = os.path.splitext(filename)
                filename = f"{base}_{pdf_name}{ext}"
            
            filepath = os.path.join(debug_dir, filename)
            with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(content)
    
    def extract_text_from_pdf(self, pdf_path):
        try:
            pdf_name = os.path.basename(pdf_path).replace('.pdf', '')
            raw_text = ""
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                page_count = len(pdf_reader.pages)

                page_texts = []
                for page_num in range(page_count):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    page_texts.append(f"=== PAGE {page_num + 1} ===\n{page_text}\n")
                    raw_text += page_text + "\n"
                
                cleaned_text = self.clean_text(raw_text, pdf_name)
                self.extracted_texts[pdf_path] = cleaned_text
                
                return cleaned_text
                
        except Exception as e:
            error_msg = f"Error extracting text from {pdf_path}: {e}"
            print(error_msg)
            self.save_debug(f"error.txt", error_msg, pdf_name)
            return ""
    
    def clean_text(self, text, pdf_name=""):
        # Step 1: Ilangin karakter goofy ahh
        replacements = {
            'ï¼': ':',          # Corrupted colon
            '：': ':',          # Full-width colon  
            'Â': '',            # Spurious character
            'â€‹': '',          # Zero-width space
            'â€"': '-',         # Em dash
            'â€™': "'",         # Smart quote
            'â€œ': '"',         # Smart quote open
            'â€': '"',          # Smart quote close
            'â—': '•',          # Bullet point
            '\xa0': ' ',        # Non-breaking space
            '\r': '',           # Carriage return
        }
        
        cleaned = text
        artifacts_found = []
        
        for old, new in replacements.items():
            count = cleaned.count(old)
            if count > 0:
                artifacts_found.append(f"'{old}' -> '{new}': {count} occurrences")
                cleaned = cleaned.replace(old, new)

        # Step 2: ilangin whitespace        
        lines = cleaned.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            line = ' '.join(line.split())
            cleaned_lines.append(line)
        
        cleaned = '\n'.join(cleaned_lines)
        
        # Step 3: ilangin line breaks
        while '\n\n\n' in cleaned:
            cleaned = cleaned.replace('\n\n\n', '\n\n')
        
        # Step 4: ilangin karakter non-printable
        cleaned = ''.join(char for char in cleaned if char.isprintable() or char == '\n')
        
        
        return cleaned.strip()
    
    def extract_all_pdfs_from_directory(self, directory_path):
        extracted_data = []
        category_count = {}
        total_files = 0
        processed_files = 0
        
        print("\n=== Scanning for PDF files ===")
        for root, dirs, files in os.walk(directory_path):
            category = os.path.basename(root)
            pdf_files = [f for f in files if f.endswith('.pdf')]
            if pdf_files:
                print(f"Found {len(pdf_files)} PDFs in {category}")
                total_files += min(len(pdf_files), 20)  
        
        print(f"\nTotal PDFs to process: {total_files}")
        print("=== Starting extraction ===\n")
        
        start_time = datetime.now()
        
        for root, dirs, files in os.walk(directory_path):
            category = os.path.basename(root)
            pdf_files = sorted([f for f in files if f.endswith('.pdf')])
            
            for file in pdf_files:
                # Limit to 20 files per category
                if category not in category_count:
                    category_count[category] = 0
                
                if category_count[category] >= 20:
                    continue
                
                pdf_path = os.path.join(root, file)
                
                # Show progress
                processed_files += 1
                print(f"[{processed_files}/{total_files}] Processing: {category}/{file}", end='')
                sys.stdout.flush()
                
                # Extract text
                text = self.extract_text_from_pdf(pdf_path)
                
                if text:
                    extracted_data.append({
                        'path': pdf_path,
                        'filename': file,
                        'text': text,
                        'category': category
                    })
                    category_count[category] += 1
                    print(" ✓")
                else:
                    print(" ✗ (failed)")
        
        # Show completion statistics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n=== Extraction Complete ===")
        print(f"Total processed: {processed_files} files")
        print(f"Successful: {len(extracted_data)} files")
        print(f"Failed: {processed_files - len(extracted_data)} files")
        print(f"Time taken: {duration:.2f} seconds")
        print(f"Average: {duration/processed_files:.2f} seconds per file")
        print("========================\n")
        
        return extracted_data
    
    def get_cached_text(self, pdf_path):
        return self.extracted_texts.get(pdf_path, None)