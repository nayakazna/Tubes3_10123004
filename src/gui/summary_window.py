from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class SummaryWindow(QDialog):
    def __init__(self, cv_data, parent=None):
        super().__init__(parent)
        self.cv_data = cv_data
        self.extracted_info = cv_data['extracted_info']
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("CV Summary")
        self.setGeometry(200, 200, 600, 700)
        
        # Set styling
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #212529;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QLabel("CV Summary")
        header_label.setFont(QFont("Arial", 18, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        
        # Personal Information
        personal_group = QGroupBox("Personal Information")
        personal_layout = QVBoxLayout()
        
        personal_info = self.extracted_info.get('personal_info', {})
        # Name
        if 'db_first_name' in self.cv_data and 'db_last_name' in self.cv_data:
            name = f"{self.cv_data['db_first_name']} {self.cv_data['db_last_name']}"
        else:
            name = personal_info.get('name', self.cv_data.get('name', 'Not found'))
        name_label = QLabel(f"<b>Name:</b> {name}")
        personal_layout.addWidget(name_label)
        
        # Phone
        if 'db_phone' in self.cv_data:
            phone = self.cv_data['db_phone']
        else:
            phone = personal_info.get('phone', 'Not found')
        phone_label = QLabel(f"<b>Phone:</b> {phone}")
        personal_layout.addWidget(phone_label)
        
        # Address - from database
        address = self.cv_data.get('db_address', 'Not found')
        address_label = QLabel(f"<b>Address:</b> {address}")
        personal_layout.addWidget(address_label)
        
        # Date of Birth - from database
        dob = self.cv_data.get('db_dob', 'Not found')
        dob_label = QLabel(f"<b>Date of Birth:</b> {dob}")
        personal_layout.addWidget(dob_label)
        
        # LinkedIn - from extraction
        if 'linkedin' in personal_info:
            linkedin_label = QLabel(f"<b>LinkedIn:</b> {personal_info['linkedin']}")
            personal_layout.addWidget(linkedin_label)
        
        personal_group.setLayout(personal_layout)
        content_layout.addWidget(personal_group)
        
        # Skills
        skills = self.extracted_info.get('skills', [])
        if skills:
            skills_group = QGroupBox("Skills")
            skills_layout = QVBoxLayout()
            
            # Create tag-like display for skills
            skills_widget = QWidget()
            skills_flow = QHBoxLayout()
            skills_flow.setSpacing(5)
            
            row_widget = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setSpacing(5)
            
            for i, skill in enumerate(skills[:15]):  # batesin ke 15
                skill_label = QLabel(skill)
                skill_label.setStyleSheet("""
                    background-color: #e9ecef;
                    padding: 5px 10px;
                    border-radius: 15px;
                    color: #495057;
                """)
                row_layout.addWidget(skill_label)
                
                # bikin baris baru setiap 5 skill
                if (i + 1) % 5 == 0:
                    row_widget.setLayout(row_layout)
                    skills_layout.addWidget(row_widget)
                    row_widget = QWidget()
                    row_layout = QHBoxLayout()
                    row_layout.setSpacing(5)
            
            # sisanya
            if row_layout.count() > 0:
                row_layout.addStretch()
                row_widget.setLayout(row_layout)
                skills_layout.addWidget(row_widget)
            
            skills_group.setLayout(skills_layout)
            content_layout.addWidget(skills_group)
        
        # Job History
        job_group = QGroupBox("Job History")
        job_layout = QVBoxLayout()
        
        experience = self.extracted_info.get('experience', [])
        if experience:
            for i, job in enumerate(experience[:5]):  # batesin ke 5 jobs
                job_label = QLabel(f"• {job}")
                job_label.setWordWrap(True)
                job_label.setStyleSheet("padding: 5px;")
                job_layout.addWidget(job_label)
        else:
            no_exp_label = QLabel("No job history found")
            no_exp_label.setStyleSheet("color: #6c757d; padding: 5px;")
            job_layout.addWidget(no_exp_label)
        
        job_group.setLayout(job_layout)
        content_layout.addWidget(job_group)
        
        # Education
        edu_group = QGroupBox("Education")
        edu_layout = QVBoxLayout()
        
        education = self.extracted_info.get('education', [])
        if education:
            for edu in education:
                edu_label = QLabel(f"• {edu}")
                edu_label.setWordWrap(True)
                edu_label.setStyleSheet("padding: 5px;")
                edu_layout.addWidget(edu_label)
        else:
            no_edu_label = QLabel("No education information found")
            no_edu_label.setStyleSheet("color: #6c757d; padding: 5px;")
            edu_layout.addWidget(no_edu_label)
        
        edu_group.setLayout(edu_layout)
        content_layout.addWidget(edu_group)
        
        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        layout.addWidget(scroll_area)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 30px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)