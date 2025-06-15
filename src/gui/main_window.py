from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os
import time
from threading import Thread
import random
from datetime import datetime, timedelta

from algorithms.kmp import KMP
from algorithms.boyer_moore import BoyerMoore
from algorithms.aho_corasick import AhoCorasick
from algorithms.levenshtein import LevenshteinDistance
from extractors.pdf_extractor import PDFExtractor
from extractors.regex_extractor import RegexExtractor
from database.models import ApplicantModel, ApplicationModel
from gui.summary_window import SummaryWindow


class CVCard(QWidget):
    def __init__(self, cv_data, parent=None):
        super().__init__(parent)
        self.cv_data = cv_data
        self.parent_window = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Card styling
        self.setStyleSheet("""
            CVCard {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
            QLabel {
                color: #212529;
            }
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
        """)
        
        # Name - Use decrypted name
        name = self.cv_data.get('name', 'Unknown')
        name_label = QLabel(f"<b>{name}</b>")
        name_label.setFont(QFont("Arial", 12))
        layout.addWidget(name_label)
        
        # Match count
        match_label = QLabel(f"{self.cv_data['match_count']} matches")
        layout.addWidget(match_label)
        
        # Keywords found
        keywords_text = ""
        for keyword, count in self.cv_data['keywords_found'].items():
            keywords_text += f"{keyword}: {count} occurrence(s)\n"
        
        keywords_label = QLabel(keywords_text.strip())
        keywords_label.setStyleSheet("color: #6c757d;")
        layout.addWidget(keywords_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        summary_btn = QPushButton("Summary")
        summary_btn.clicked.connect(self.show_summary)
        button_layout.addWidget(summary_btn)
        
        view_cv_btn = QPushButton("View CV")
        view_cv_btn.clicked.connect(self.view_cv)
        button_layout.addWidget(view_cv_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setMaximumHeight(200)
    
    def show_summary(self):
        """Show CV summary window"""
        summary_window = SummaryWindow(self.cv_data, self)
        summary_window.show()
    
    def view_cv(self):
        """Open CV file"""
        try:
            if sys.platform == "win32":
                os.startfile(self.cv_data['path'])
            elif sys.platform == "darwin":
                os.system(f"open {self.cv_data['path']}")
            else:
                os.system(f"xdg-open {self.cv_data['path']}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cannot open CV: {str(e)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pdf_extractor = PDFExtractor()
        self.regex_extractor = RegexExtractor()
        self.kmp = KMP()
        self.boyer_moore = BoyerMoore()
        self.aho_corasick = AhoCorasick()
        self.levenshtein = LevenshteinDistance()
        
        self.cv_data = []
        self.current_algorithm = "KMP"
        
        self.init_ui()
        self.load_cv_data()
    
    def init_ui(self):
        self.setWindowTitle("CV Analyzer App")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QLabel {
                color: #212529;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0066cc;
            }
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QRadioButton {
                font-size: 14px;
                padding: 5px;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title_label = QLabel("CV Analyzer App")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("margin-bottom: 20px;")
        main_layout.addWidget(title_label)
        
        # Keywords input
        keywords_label = QLabel("Keywords:")
        keywords_label.setFont(QFont("Arial", 12))
        main_layout.addWidget(keywords_label)
        
        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("React, Express, HTML")
        main_layout.addWidget(self.keywords_input)
        
        # Algorithm selection
        algo_label = QLabel("Search Algorithm:")
        algo_label.setFont(QFont("Arial", 12))
        algo_label.setStyleSheet("margin-top: 20px;")
        main_layout.addWidget(algo_label)
        
        algo_layout = QHBoxLayout()
        
        self.kmp_radio = QRadioButton("KMP")
        self.kmp_radio.setChecked(True)
        self.kmp_radio.toggled.connect(lambda: self.set_algorithm("KMP"))
        algo_layout.addWidget(self.kmp_radio)
        
        self.bm_radio = QRadioButton("BM")
        self.bm_radio.toggled.connect(lambda: self.set_algorithm("BM"))
        algo_layout.addWidget(self.bm_radio)
        
        self.ac_radio = QRadioButton("Aho-Corasick")
        self.ac_radio.toggled.connect(lambda: self.set_algorithm("AC"))
        algo_layout.addWidget(self.ac_radio)
        
        algo_layout.addStretch()
        main_layout.addLayout(algo_layout)
        
        # Top matches selector
        matches_label = QLabel("Top Matches:")
        matches_label.setFont(QFont("Arial", 12))
        matches_label.setStyleSheet("margin-top: 20px;")
        main_layout.addWidget(matches_label)
        
        self.matches_spinner = QSpinBox()
        self.matches_spinner.setMinimum(1)
        self.matches_spinner.setMaximum(100)
        self.matches_spinner.setValue(5)
        self.matches_spinner.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 2px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        main_layout.addWidget(self.matches_spinner)
        
        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_cvs)
        self.search_button.setStyleSheet("margin-top: 20px; padding: 12px 30px;")
        main_layout.addWidget(self.search_button, alignment=Qt.AlignCenter)
        
        # Results section
        results_label = QLabel("Results")
        results_label.setFont(QFont("Arial", 16, QFont.Bold))
        results_label.setStyleSheet("margin-top: 30px; margin-bottom: 10px;")
        main_layout.addWidget(results_label)
        
        # Time summary
        self.time_label = QLabel("")
        self.time_label.setStyleSheet("color: #6c757d; margin-bottom: 10px;")
        main_layout.addWidget(self.time_label)
        
        # Results scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
        """)
        
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout()
        self.results_widget.setLayout(self.results_layout)
        
        scroll_area.setWidget(self.results_widget)
        main_layout.addWidget(scroll_area)
        
        central_widget.setLayout(main_layout)
        
    def set_algorithm(self, algorithm):
        """Set the current search algorithm"""
        self.current_algorithm = algorithm
        
    def seed_database_for_loaded_cvs(self):
        """Seed database with manual data for each loaded CV"""
        try:
            applicant_model = ApplicantModel()
            application_model = ApplicationModel()
            
            # Sample data for seeding
            first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'Robert', 'Lisa', 'James', 'Mary']
            last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Martinez', 'Anderson']
            cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego']
            states = ['NY', 'CA', 'IL', 'TX', 'AZ', 'PA', 'TX', 'CA']
            
            print("\n=== Seeding Database ===")
            
            for i, cv in enumerate(self.cv_data):
                # Generate random data
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                
                # Generate random birthdate (25-50 years old)
                age = random.randint(25, 50)
                birth_date = datetime.now() - timedelta(days=age*365)
                
                # Generate random address
                street_num = random.randint(100, 9999)
                street_name = random.choice(['Main St', 'Oak Ave', 'Elm St', 'Park Blvd', 'First Ave'])
                city = random.choice(cities)
                state = states[cities.index(city)]
                address = f"{street_num} {street_name}, {city}, {state}"
                
                # Generate random phone
                phone = f"+1{random.randint(200, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}"
                
                # Create applicant (data will be encrypted)
                applicant_id = applicant_model.create_applicant(
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=birth_date.strftime('%Y-%m-%d'),
                    address=address,
                    phone_number=phone
                )
                
                # Create application
                application_model.create_application(
                    applicant_id=applicant_id,
                    application_role=cv['category'],
                    cv_path=cv['path']
                )
                
                # Store applicant_id in cv data
                cv['applicant_id'] = applicant_id
                
                print(f"Seeded: {first_name} {last_name} - {cv['filename']}")
            
            applicant_model.close()
            application_model.close()
            
            print("=== Database Seeding Complete ===\n")
            
        except Exception as e:
            print(f"Error seeding database: {e}")
    
    def load_cv_data(self):
        """Load CV data from the data folder with progress dialog"""
        base_dir = os.path.dirname(__file__)
        data_path = os.path.join(base_dir, "..", "..", "data", "data")
        data_path = os.path.abspath(data_path)
        
        if not os.path.exists(data_path):
            QMessageBox.warning(self, "Warning", f"Data folder not found: {data_path}")
            return
        
        # Create progress dialog
        progress = QProgressDialog("Loading CV files...", "Cancel", 0, 100, self)
        progress.setWindowTitle("Loading CVs")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        
        # Create loading thread
        class LoaderThread(QThread):
            progress_update = pyqtSignal(int, str)
            finished_signal = pyqtSignal(list)
            
            def __init__(self, pdf_extractor, regex_extractor, data_path):
                super().__init__()
                self.pdf_extractor = pdf_extractor
                self.regex_extractor = regex_extractor
                self.data_path = data_path
            
            def run(self):
                # Extract text from all PDFs
                cv_data = self.pdf_extractor.extract_all_pdfs_from_directory(self.data_path)
                
                # Process with regex extractor
                total = len(cv_data)
                for i, cv in enumerate(cv_data):
                    self.progress_update.emit(int((i / total) * 100), f"Processing {cv['filename']}...")
                    
                    cv['extracted_info'] = self.regex_extractor.extract_all(cv['text'])
                    
                    # Get name from extracted info or filename
                    personal_info = cv['extracted_info'].get('personal_info', {})
                    cv['name'] = personal_info.get('name', cv['filename'].replace('.pdf', ''))
                
                self.finished_signal.emit(cv_data)
        
        # Create and start loader thread
        self.loader_thread = LoaderThread(self.pdf_extractor, self.regex_extractor, data_path)
        
        def update_progress(value, text):
            progress.setValue(value)
            progress.setLabelText(text)
            if progress.wasCanceled():
                self.loader_thread.terminate()
        
        def loading_finished(cv_data):
            self.cv_data = cv_data
            progress.close()
            
            # Seed database
            # self.seed_database_for_loaded_cvs()
            
            # Load and decrypt data from database for each CV
            self.load_database_info()
            
            QMessageBox.information(self, "Success", f"Loaded {len(self.cv_data)} CVs successfully!")
        
        self.loader_thread.progress_update.connect(update_progress)
        self.loader_thread.finished_signal.connect(loading_finished)
        self.loader_thread.start()
    
    def load_database_info(self):
        """Load and decrypt information from database for all CVs"""
        applicant_model = ApplicantModel()
        
        for cv in self.cv_data:
            if 'applicant_id' in cv:
                # Get decrypted applicant data
                applicant = applicant_model.get_applicant(cv['applicant_id'])
                if applicant:
                    # Store decrypted data
                    cv['db_first_name'] = applicant.get('first_name', '')
                    cv['db_last_name'] = applicant.get('last_name', '')
                    cv['db_phone'] = applicant.get('phone_number', '')
                    cv['db_address'] = applicant.get('address', '')
                    
                    # Format DOB
                    dob = applicant.get('date_of_birth')
                    cv['db_dob'] = dob.strftime('%Y-%m-%d') if dob else "Not found"
                    
                    # Update name with decrypted data
                    cv['name'] = f"{cv['db_first_name']} {cv['db_last_name']}".strip()
        
        applicant_model.close()
    
    def search_cvs(self):
        """Perform CV search based on keywords"""
        keywords_text = self.keywords_input.text().strip()
        
        if not keywords_text:
            QMessageBox.warning(self, "Warning", "Please enter keywords")
            return
        
        # Clear previous results
        for i in reversed(range(self.results_layout.count())): 
            self.results_layout.itemAt(i).widget().setParent(None)
        
        # Parse keywords
        keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
        
        # Perform search
        start_time = time.time()
        
        if self.current_algorithm == "KMP":
            algorithm = self.kmp
        elif self.current_algorithm == "BM":
            for kw in keywords:
                self.boyer_moore.preprocess_pattern(kw.lower())
            algorithm = self.boyer_moore
        else:  # Aho-Corasick
            algorithm = self.aho_corasick
        
        # Exact match search
        exact_results = []

        if self.current_algorithm == "AC":
            ac_root = self.aho_corasick.build_automaton(keywords)
        
        for cv in self.cv_data:
            if self.current_algorithm == "AC":
                # Aho-Corasick handles multiple patterns efficiently
                matches = algorithm.search_multiple(cv['text'], keywords, root=ac_root)
            else:
                # KMP and BM search patterns one by one
                matches = algorithm.search_multiple(cv['text'], keywords)
            
            if matches:
                total_count = sum(match['count'] for match in matches.values())
                exact_results.append({
                    'cv': cv,
                    'matches': matches,
                    'total_count': total_count
                })
        
        exact_time = time.time() - start_time
        
        # Fuzzy match search for keywords not found
        fuzzy_start = time.time()
        fuzzy_results = []
        
        # Find keywords that weren't found in exact match
        all_found_keywords = set()
        for result in exact_results:
            all_found_keywords.update(result['matches'].keys())
        
        missing_keywords = set(keywords) - all_found_keywords
        
        if missing_keywords:
            for cv in self.cv_data:
                fuzzy_matches = self.levenshtein.fuzzy_search(cv['text'], list(missing_keywords))
                
                if fuzzy_matches:
                    fuzzy_count = sum(len(matches) for matches in fuzzy_matches.values())
                    fuzzy_results.append({
                        'cv': cv,
                        'fuzzy_matches': fuzzy_matches,
                        'fuzzy_count': fuzzy_count
                    })
        
        fuzzy_time = time.time() - fuzzy_start
        
        # Combine and sort results
        all_results = []
        
        # Add exact match results
        for result in exact_results:
            cv_result = {
                'path': result['cv']['path'],
                'name': result['cv']['name'],  # This now has decrypted name
                'match_count': result['total_count'],
                'keywords_found': {k: v['count'] for k, v in result['matches'].items()},
                'unique_keywords_matched': len(result['matches']),
                'extracted_info': result['cv']['extracted_info'],
                'text': result['cv']['text'],
                'applicant_id': result['cv'].get('applicant_id'),
                'db_first_name': result['cv'].get('db_first_name', ''),
                'db_last_name': result['cv'].get('db_last_name', ''),
                'db_phone': result['cv'].get('db_phone', ''),
                'db_address': result['cv'].get('db_address', ''),
                'db_dob': result['cv'].get('db_dob', '')
            }
            all_results.append(cv_result)
        
        # Add fuzzy match results (if not already in exact results)
        exact_paths = {r['path'] for r in all_results}
        
        for result in fuzzy_results:
            if result['cv']['path'] not in exact_paths:
                cv_result = {
                    'path': result['cv']['path'],
                    'name': result['cv']['name'],  # This now has decrypted name
                    'match_count': result['fuzzy_count'],
                    'keywords_found': {k: f"{len(v)} fuzzy matches" for k, v in result['fuzzy_matches'].items()},
                    'unique_keywords_matched': len(result['fuzzy_matches']),
                    'extracted_info': result['cv']['extracted_info'],
                    'text': result['cv']['text'],
                    'applicant_id': result['cv'].get('applicant_id'),
                    'db_first_name': result['cv'].get('db_first_name', ''),
                    'db_last_name': result['cv'].get('db_last_name', ''),
                    'db_phone': result['cv'].get('db_phone', ''),
                    'db_address': result['cv'].get('db_address', ''),
                    'db_dob': result['cv'].get('db_dob', '')
                }
                all_results.append(cv_result)
        
        # Sort by unique keywords matched, then by match count
        all_results.sort(key=lambda x: (x['unique_keywords_matched'], x['match_count']), reverse=True)
        
        # Display top N results
        top_n = self.matches_spinner.value()
        display_results = all_results[:top_n]
        
        # Update time label
        total_cvs = len(self.cv_data)
        self.time_label.setText(
            f"Exact Match: {total_cvs} CVs scanned in {exact_time*1000:.0f}ms.\n"
            f"Fuzzy Match: {total_cvs} CVs scanned in {fuzzy_time*1000:.0f}ms."
        )
        
        # Display results
        if display_results:
            for result in display_results:
                card = CVCard(result, self)
                self.results_layout.addWidget(card)
        else:
            no_results_label = QLabel("No matching CVs found")
            no_results_label.setAlignment(Qt.AlignCenter)
            no_results_label.setStyleSheet("color: #6c757d; padding: 20px;")
            self.results_layout.addWidget(no_results_label)